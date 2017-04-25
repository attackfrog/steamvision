import os
import datetime

import urllib.request, urllib.parse
import json
from flask import jsonify, render_template, g
import psycopg2
import lxml
from bs4 import BeautifulSoup


def get_db():
    """Returns a database connection, connecting to the database if necessary."""

    db = getattr(g, '_database', None)
    if db is None:
        # Connect to database
        urllib.parse.uses_netloc.append("postgres")
        url = urllib.parse.urlparse(os.environ["DATABASE_URL"])
        db = g._database = psycopg2.connect(
            database=url.path[1:],
            user=url.username,
            password=url.password,
            host=url.hostname,
            port=url.port
        )
    return db


def get_user_games(user_id):
    """Gets user information from Steam API."""

    # Attempt to convert user_id to a Steam ID, if it isn't one
    steam_id = guess_steam_id(user_id)

    # Try accessing the user's games list
    try:
        api_info = json.load(urllib.request.urlopen(
            "http://api.steampowered.com/IPlayerService/GetOwnedGames/v0001/?key={}&steamid={}&include_appinfo=1"
            .format(os.environ.get("API_KEY"), steam_id)))

    # If it didn't work, return an error value
    except:
        return ('', 204)

    return jsonify(api_info["response"])


def get_user_profile(user_id):
    """Gets user profile information from Steam API."""

    # Attempt to convert user_id to a Steam ID, if it isn't one
    steam_id = guess_steam_id(user_id)

    # Try accessing user's profile information
    try:
        api_info = json.load(urllib.request.urlopen(
            "http://api.steampowered.com/ISteamUser/GetPlayerSummaries/v0002/?key={}&steamids={}"
            .format(os.environ.get("API_KEY"), steam_id)))

    # If it didn't work, return an error value
    except:
        return ('', 204)

    return jsonify(api_info["response"]["players"][0])


def guess_steam_id(user_id):
    """Returns a best guess for a user's Steam ID, from a few different input types."""

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

    return steam_id


def get_game_info(appid):
    """Gets game categories and ratings from the database, or scrapes it from a Steam Store game page if missing."""

    # Get database connection and open cursor
    connection = get_db()
    cursor = connection.cursor()

    # Check if game is in database & if it's there and the data is <30 days old, return that information
    cursor.execute("SELECT * FROM games WHERE appid=%(appid)s", {"appid": appid})
    row = cursor.fetchone()
    if row is not None and row[8] + datetime.timedelta(30) > datetime.datetime.now():

        # Close cursor
        cursor.close()

        # Return info from database
        return jsonify({
            "categories": row[3],
            "ratings": [{"summary": row[4], "details": row[5]}, {"summary": row[6], "details": row[7]}],
            "description": row[2]
        })

    # Attempt to get html document for requested game's page
    try:
        page = urllib.request.urlopen("http://store.steampowered.com/app/{}/".format(appid))
    except:
        raise RuntimeError("Failed to open http://store.steampowered.com/app/{}/".format(appid))

    # Load page into the magical html scraper
    soup = BeautifulSoup(page, "lxml")

    # Check if we got the Store homepage: if we did the game is missing for some reason
    if not soup.title.contents[0].endswith("on Steam"):
        categories = ["Missing?"]
        ratings = [{"summary": "", "details": ""}, {"summary": "", "details": ""}]
        description = "This game seems to have vanished from the Steam Store."

    # See if it the appid is hidden behind an age check gate & return dummy data (but real description) if it is
    elif "agecheck" in soup.body["class"]:
        categories = ["Age Check"]
        ratings = [{"summary": "", "details": ""}, {"summary": "", "details": ""}]
        description = get_description(soup)

    # If it actually is the page we were looking for, scrape the information from it
    else:
        categories = get_categories(soup)
        ratings = get_ratings(soup)
        description = get_description(soup)

    # Insert the game's information into the database
    cursor.execute(("INSERT INTO games VALUES (%(appid)s, %(appname)s, %(description)s, %(categories)s, "
                    "%(ratings_recent_summary)s, %(ratings_recent_details)s, %(ratings_overall_summary)s, "
                    "%(ratings_overall_details)s, %(updated)s)"),
                   {
                       "appid": appid,
                       "appname": soup.title.contents[0].replace(" on Steam", ""),   # Get game name from page title
                       "description": description,
                       "categories": categories,
                       "ratings_recent_summary": ratings[0]["summary"],
                       "ratings_recent_details": ratings[0]["details"],
                       "ratings_overall_summary": ratings[1]["summary"],
                       "ratings_overall_details": ratings[1]["details"],
                       "updated": datetime.datetime.now()
                   })

    # Close database connection
    cursor.close()
    connection.commit()

    # Return JSON of information
    return jsonify({
        "categories": categories,
        "ratings": ratings,
        "description": description
    })


def get_categories(soup):
    """Scrapes category information from a parsed Steam Store game page."""

    # Get appropriate <div> and check that it exists
    div = soup.find(class_="glance_tags")
    if div is None:
        # If not, this may be an age check page that displays categories
        div = soup.find(class_="agegate_tags")
        if div is None:
            raise RuntimeError("The Steam Store layout changed! Missing \"glance_tags\" and \"agegate_tags\", (page title: {})"
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

    # Define blank item
    blank = {
        "summary": "",
        "details": ""
    }

    # Extract summary (eg. "Mixed") and detailed info (eg. "55% of 18 user reviews...") from divs
    for div in divs:

        # Ignore divs that don't have these characteristics
        try:
            # Also ignore the div if it is at the bottom, by the reviews section
            if not div.find_next()["class"][0] == "loading_more_reviews":

                info.append({
                    "summary": div.contents[0],
                    "details": div["data-store-tooltip"]
                })
        except:
            pass

    # If just one set was found, it's probably overall reviews, so insert a blank entry for recent
    if len(info) == 1:
        info.insert(0, blank)

        # Unless there's not enough reviews to generate a score, in which case don't keep the entry
        if info[1]["details"] == "Need more user reviews to generate a score":
            info.pop()
            info.append(blank)

    # If none of them had those characteristics, it's because the page is missing either recent reviews or any reviews
    elif len(info) == 0:

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
