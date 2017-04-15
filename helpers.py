import os
import datetime

import urllib.request, urllib.parse
import json
from flask import jsonify, render_template
import psycopg2
import lxml
from bs4 import BeautifulSoup


def get_user_info(user_id):
    """Gets user information from Steam API, accepting several user id input types."""

    # Check whether it's a Steam ID of the format Steam_0:1:12345678
    if user_id[:6].lower() == "steam_" and user_id[7:8] == ":" and user_id[9:10] == ":":
        # If so, convert it to a 64bit SteamID
        steam_id = int(user_id[10:]) * 2 + int(0x0110000100000000) + int(user_id[8:9])

    # If it isn't, check if it's a vanity URL
    else:
        if "steamcommunity.com/id/" in user_id:
            # If it is, remove the URL part if present
            while user_id[len(user_id) - 1] == "/":
                user_id = user_id[:len(user_id) - 1]
            user_id = user_id[user_id.rfind("/") + 1:]

        # Try vanity in Steam API
        user_id_info = json.load(urllib.request.urlopen(
            "http://api.steampowered.com/ISteamUser/ResolveVanityURL/v0001/?key={}&vanityurl={}"
            .format(os.environ.get("API_KEY"), user_id)))

        # If it works, we've got the SteamID
        if user_id_info["response"]["success"] == 1:
            steam_id = user_id_info["response"]["steamid"]

        # If it isn't, hopefully they gave us a 64bit SteamID
        else:
            steam_id = user_id

    # Try accessing the user's games list
    try:
        api_info = json.load(urllib.request.urlopen(
            "http://api.steampowered.com/IPlayerService/GetOwnedGames/v0001/?key={}&steamid={}&include_appinfo=1&format=json"
            .format(os.environ.get("API_KEY"), steam_id)))

    # If it didn't work, give an error
    except:
        message = "That doesn't seem to be a valid Steam ID."
        return render_template("error.html", message=message)

    # If the account has no games, tell the user
    api_info = api_info["response"]
    if api_info["game_count"] == 0:
        message = "That account doesn't have any games!"
        return render_template("error.html", message=message)

    return merge_game_info(api_info)


def merge_game_info(api_info):
    """Merges game information into one JSON structure, and adds it to the database if necessary."""

    # Initialize return structure
    user_info = {
        "games_count": api_info["game_count"],
        "games": []
    }

    # Connect to database
    urllib.parse.uses_netloc.append("postgres")
    url = urllib.parse.urlparse(os.environ["DATABASE_URL"])
    connection = psycopg2.connect(
        database=url.path[1:],
        user=url.username,
        password=url.password,
        host=url.hostname,
        port=url.port
    )
    cursor = connection.cursor()

    # Iterate through all games in user's library
    for game in api_info["games"]:

        # Check if game is in database
        cursor.execute("SELECT appid FROM games WHERE appid = %s;", (game["appid"],))
        row = cursor.fetchone()

        # If it's not, or the entry is more than 30 days old, insert the game
        if row is None or (row[10] - datetime.datetime.now()).days > 30:
            # Scrape game info from store webpage
            game_scrape = get_game_info(game["appid"])

            # Combine info into one structure
            game_info = {
                "appid": game["appid"],
                "appname": game["name"],
                "description": game_scrape["description"],
                "img_icon_url": game["img_icon_url"],
                "img_logo_url": game["img_logo_url"],
                "categories": game_scrape["categories"],
                "ratings_recent_summary": game_scrape["ratings"][0]["summary"],
                "ratings_recent_details": game_scrape["ratings"][0]["details"],
                "ratings_overall_summary": game_scrape["ratings"][1]["summary"],
                "ratings_overall_details": game_scrape["ratings"][1]["details"]
            }
            # Insert info into database
            cursor.execute("""INSERT INTO games VALUES (%(appid)s, %(appname)s, %(description)s, %(categories)s,
                              %(ratings_recent_summary)s, %(ratings_recent_details)s, %(ratings_overall_summary)s, 
                              %(ratings_overall_details)s, %(updated)s);""",
                           {"appid": game_info["appid"],
                            "appname": game_info["appname"],
                            "description": game_info["description"],
                            "categories": game_info["categories"],
                            "ratings_recent_summary": game_info["ratings_recent_summary"],
                            "ratings_recent_details": game_info["ratings_recent_details"],
                            "ratings_overall_summary": game_info["ratings_overall_summary"],
                            "ratings_overall_details": game_info["ratings_overall_details"],
                            "updated": datetime.datetime.now()
                            })

        # If the game was in the database, retrieve the information from there
        else:
            game_info = {
                "appid": game["appid"],
                "appname": game["name"],
                "description": row[2],
                "img_icon_url": game["img_icon_url"],
                "img_logo_url": game["img_logo_url"],
                "categories": row[3],
                "ratings_recent_summary": row[4],
                "ratings_recent_details": row[5],
                "ratings_overall_summary": row[6],
                "ratings_overall_details": row[7]
            }

        # Add info to user's games list
        user_info["games"].append(game_info)

    # Commit changes and close database connection
    cursor.close()
    connection.commit()
    connection.close()

    return jsonify(user_info)


def get_game_info(appid):
    """Scrapes game category and ratings information from a Steam Store game page."""

    # Attempt to get html document for requested game's page
    try:
        page = urllib.request.urlopen("http://store.steampowered.com/app/{}/".format(appid))
    except:
        raise RuntimeError("Failed to open http://store.steampowered.com/app/{}/".format(appid))

    # Load page into the magical html scraper
    soup = BeautifulSoup(page, "lxml")

    # Make sure the appid was valid and we didn't just get the Steam homepage
    if soup.title.contents[0] == "Welcome to Steam":
        raise RuntimeError("No Store page for http://store.steampowered.com/app/{}/".format(appid))
    elif "agecheck" in soup.body["class"]:
        return {
            "categories": ["Age Check"],
            "ratings": [{"summary": "", "details": ""}, {"summary": "", "details": ""}],
            "description": get_description(soup)
        }

    return {
        "categories": get_categories(soup),
        "ratings": get_ratings(soup),
        "description": get_description(soup)
    }


def get_categories(soup):
    """Scrapes category information from a parsed Steam Store game page."""

    # Get appropriate <div> and check that it exists
    div = soup.find(class_="glance_tags")
    if div is None:
        raise RuntimeError("The Steam Store layout changed! Missing \"glance_tags\", (page title: {})"
                           .format(soup.title.contents[0]))
    tag_type = type(div)

    # Create list
    categories = []

    # Extract categories from <div> into list:
    for item in div.contents:
        # Ignore the outer items that aren't inner tags
        if type(item) == tag_type:
            # Get the contents of the tag and strip white space
            category = item.contents[0].strip()
            # If it's not the "add a category" button, append to categories list
            if not category == "+":
                categories.append(category)

    return categories


def get_ratings(soup):
    """Scrapes ratings summary information from a parsed Steam Store game page."""

    # Get appropriate <div>s and check that they exist
    divs = soup.find_all(class_="game_review_summary")
    if divs is None:
        raise RuntimeError("The Steam Store layout changed! Missing \"game_review_summary\", (page title: {})"
                           .format(soup.title.contents[0]))

    # Create list
    info = []

    # Extract summary (eg. "Mixed") and detailed info (eg. "55% of 18 user reviews...") from divs
    for div in divs:
        # Ignore divs that don't have these characteristics
        try:
            info.append({
                "summary": div.contents[0],
                "details": div["data-store-tooltip"]
            })
        except:
            pass

    # Throw away the third set if it's there: it seems to be from a custom filter option on the page
    if len(info) == 3:
        info.pop()

    # If none of them had those characteristics, it's because the page is missing either recent reviews or any reviews
    elif len(info) == 0:
        # Define blank item
        blank = {
            "summary": "",
            "details": ""
        }
        # Get the detailed info from this div instead
        div = soup.find_all(class_="responsive_reviewdesc")
        if div is None:
            raise RuntimeError("The Steam Store layout changed! Missing \"responsive_reviewdesc\", (page title: {})"
                               .format(soup.title.contents[0]))

        # If even that didn't find anything, there are no reviews for this item
        elif len(div) == 0:
            info.append(blank)
            info.append(blank)

        # If it did find something, we're just missing recent reviews
        else:
            info.append(blank)
            info.append({
                "summary": divs[0].contents[0],
                "details": div[0].contents[0].strip()[2:]   # Slice to get rid of the "- "
            })

    return info


def get_description(soup):
    """Scrapes description snippet from a parsed Steam Store game page."""

    # Get appropriate <div> and check that it exists
    div = soup.select("[name='Description']")
    if div is None:
        raise RuntimeError("The Steam Store layout changed! Missing \"Description\", (page title: {})"
                           .format(soup.title.contents[0]))

    # Return its contents
    return div[0].attrs["content"]
