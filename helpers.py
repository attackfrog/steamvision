import os
import datetime

import urllib.request, urllib.parse
from http.client import NO_CONTENT
import json
from flask import jsonify, g
import psycopg2
import lxml
from bs4 import BeautifulSoup


def get_db():
    """Returns a database connection, connecting to the database if necessary."""

    # Get connection from global storage, if it exists
    db = getattr(g, '_database', None)

    # If it doesn't, connect to the database and store the connection in global storage
    if db is None:
        urllib.parse.uses_netloc.append("postgres")
        url = urllib.parse.urlparse(os.environ["DATABASE_URL"])
        db = g._database = psycopg2.connect(
            database=url.path[1:],
            user=url.username,
            password=url.password,
            host=url.hostname,
            port=url.port
        )
    # Return the database connection
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

    # If it didn't work, return an error value (HTTP "No Content")
    except:
        return "", NO_CONTENT

    return jsonify(api_info["response"])


def get_user_profile(user_id):
    """Gets user profile information from Steam API."""

    # Attempt to convert user_id to a Steam ID, if it isn't one
    steam_id = guess_steam_id(user_id)

    # Try accessing user's profile information
    api_info = json.load(urllib.request.urlopen(
        "http://api.steampowered.com/ISteamUser/GetPlayerSummaries/v0002/?key={}&steamids={}"
        .format(os.environ.get("API_KEY"), steam_id)))

    # If it didn't work, return an error value (HTTP "No Content")
    if len(api_info["response"]["players"]) == 0:
        return "", NO_CONTENT

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

    # Query database for game
    cursor.execute("SELECT * FROM games WHERE appid=%(appid)s", {"appid": appid})
    row = cursor.fetchone()

    # If it's there and the data is <14 days old, return that information
    if row is not None:
        if row[9] + datetime.timedelta(14) > datetime.datetime.now():
            # Close cursor
            cursor.close()

            # Return info from database
            return jsonify({
                "categories": row[3],
                "ratings": [{"summary": row[4], "details": row[5]}, {"summary": row[6], "details": row[7]}],
                "description": row[2],
                "release_date": row[8]
            })
        # If the data is >14 days old, delete it from the table
        else:
            cursor.execute("DELETE FROM games WHERE appid=%(appid)s", {"appid": appid})

    # Attempt to get html document for requested game's page
    try:
        page = urllib.request.urlopen("http://store.steampowered.com/app/{}/".format(appid))
    except:
        raise RuntimeError("Failed to open http://store.steampowered.com/app/{}/".format(appid))

    # Load page into the magical html scraper
    soup = BeautifulSoup(page, "lxml")

    # Check if we got the Store homepage: if we did the game is missing for some reason
    if not soup.title.string.endswith("on Steam"):
        categories = ["(Missing)"]
        ratings = [{"summary": "", "details": ""}, {"summary": "", "details": ""}]
        description = "This game seems to have vanished from the Steam Store."
        release_date= "(Unknown)"

    # If the page is hidden behind an age check gate (enter birthday type) return description but dummy data for others
    elif "agecheck" in soup.body["class"]:
        categories = ["(Age Check)"]
        ratings = [{"summary": "", "details": ""}, {"summary": "", "details": ""}]
        description = get_description(soup)
        release_date= "(Unknown)"

    # If the page is behind the other type of age gate (continue/cancel) return description, categories & dummy ratings
    elif soup.find(id="app_agegate") is not None:
        categories = get_categories(soup)
        ratings = [{"summary": "", "details": ""}, {"summary": "", "details": ""}]
        description = get_description(soup)
        release_date = "(Unknown)"

    # If it actually is the page we were looking for, scrape the information from it
    else:
        categories = get_categories(soup)
        ratings = get_ratings(soup)
        description = get_description(soup)
        release_date = get_release_date(soup)

    # Insert the game's information into the database
    cursor.execute(("INSERT INTO games VALUES (%(appid)s, %(appname)s, %(description)s, %(categories)s, "
                    "%(ratings_recent_summary)s, %(ratings_recent_details)s, %(ratings_overall_summary)s, "
                    "%(ratings_overall_details)s, %(release_date)s, %(updated)s)"),
                   {
                       "appid": appid,
                       "appname": soup.title.contents[0].replace(" on Steam", ""),   # Get game name from page title
                       "description": description,
                       "categories": categories,
                       "ratings_recent_summary": ratings[0]["summary"],
                       "ratings_recent_details": ratings[0]["details"],
                       "ratings_overall_summary": ratings[1]["summary"],
                       "ratings_overall_details": ratings[1]["details"],
                       "release_date": release_date,
                       "updated": datetime.datetime.now()
                   })

    # Close database connection
    cursor.close()
    connection.commit()

    # Return JSON of information
    return jsonify({
        "categories": categories,
        "ratings": ratings,
        "description": description,
        "release_date": release_date
    })


def get_categories(soup):
    """Scrapes category information from a parsed Steam Store game page."""

    # Get appropriate <div> and check that it exists
    div = soup.find(class_="glance_tags")
    if div is None:
        # If not, this may be an age check page that displays categories
        div = soup.find(class_="agegate_tags")
        if div is None:
            raise RuntimeError("The Steam Store layout changed! "
                               "Missing \"glance_tags\" and \"agegate_tags\", (page title: {})"
                               .format(soup.title.contents[0]))

    # Create list
    categories = []

    # Extract categories from <div> into list:
    tags = div.find_all("a")
    for tag in tags:
        categories.append(tag.string.strip())

    return categories


def get_ratings(soup):
    """Scrapes ratings summary information from a parsed Steam Store game page."""

    # Get appropriate <div>s and check that they exist
    divs = soup.find_all(class_="game_review_summary")

    # Create list and define blank ratings item
    info = []
    blank = {
        "summary": "",
        "details": ""
    }

    # Extract summary (eg. "Mixed") and detailed info (eg. "55% of 18 user reviews...") from divs
    for div in divs:

        try:
            # Ignore the div if it is at the bottom, by the reviews section
            if "loading_more_reviews" not in div.find_next()["class"]:

                # Get summary info from div and details from its companion, if it exists
                summary = div.string
                try:
                    # For the details, strip the whitespace and "- " from its content
                    details = div.find_next_sibling(class_="responsive_reviewdesc").string.strip()[2:]
                # If it doesn't exist, skip this div
                except AttributeError:
                    continue

                # Append the info to the info list
                info.append({
                    "summary": summary,
                    "details": details
                })
        # If the next div doesn't have a class, skip this div
        except KeyError:
            continue

    # If just one set was found, it's probably overall reviews, so insert a blank entry for recent
    if len(info) == 1:
        info.insert(0, blank)

        # Unless there's not enough reviews to generate a score, in which case don't keep the entry
        if info[1]["details"] == "Need more user reviews to generate a score":
            info.pop()
            info.append(blank)

    # If no sets were found, insert blank values for both
    elif len(info) == 0:
        info.append(blank)
        info.append(blank)

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


def get_release_date(soup):
    """Scrapes the release date from a Steam Store game page."""

    # Get the appropriate div and check that it exists
    div = soup.find(class_="release_date")
    if div is None:
        # If there's no release date, just return (Unknown)
        return "(Unknown)"

    # Otherwise, return the date portion of the div (format: Aug. 21, 2012)
    return div.find(class_="date").string
