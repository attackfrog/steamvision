import os
import urllib.request
import json

from flask import Flask, jsonify, render_template, request, url_for
from flask_jsglue import JSGlue

from helpers import get_categories

# configure application
app = Flask(__name__)
JSGlue(app)


@app.route("/")
def index():
    """Display welcome page."""
    return render_template("index.html")

@app.route("/user")
def user():
    """Get info from Steam API about a steam user."""

    # Make sure (Steam) API key is set, just in case something has gone horribly wrong
    if not os.environ.get("API_KEY"):
        raise RuntimeError("API Key not set.")

    # Make sure an id was provided
    if not request.args.get("id"):
        message = "You didn't provide an ID."
        return render_template("error.html", message=message)

    # Put the id in a variable to make it more succinct to access
    user_id = request.args.get("id")

    # Check whether it's a Steam ID of the format Steam_0:1:12345678
    if user_id[:6].lower() == "steam_" and user_id[7:8] == ":" and user_id[9:10] == ":":
        # If so, convert it to a 64bit SteamID
        steam_id = int(user_id[10:])*2 + int(0x0110000100000000) + int(user_id[8:9])

    # If it isn't, check if it's a vanity URL
    else:
        if "steamcommunity.com/id/" in user_id:
            # If it is, remove the URL part if present
            while user_id[len(user_id) - 1] == "/":
                user_id = user_id[:len(user_id) - 1]
            user_id = user_id[user_id.rfind("/")+1:]


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
        games_info = json.load(urllib.request.urlopen("http://api.steampowered.com/IPlayerService/GetOwnedGames/v0001/?key={}&steamid={}&include_appinfo=1&format=json"
                               .format(os.environ.get("API_KEY"), steam_id)))
    # If it didn't work, give an error
    except:
        message = "That doesn't seem to be a valid Steam ID."
        return render_template("error.html", message=message)

    # If the account has no games, tell the user
    if games_info["response"]["game_count"] == 0:
        message = "That account doesn't have any games!"
        return render_template("error.html", message=message)

    return jsonify(games_info["response"])

@app.route("/addgame")
def addgame():
    """Adds information about a game by Steam appid to the database."""

    # Make sure an appid was provided
    if not request.args.get("appid"):
        raise RuntimeError("Missing appid")

    # Get webpage for appid
    try:
        page = urllib.request.urlopen("http://store.steampowered.com/app/{}/".format(appid))
    except:
        raise RuntimeError("Failed to open http://store.steampowered.com/app/{}/".format(appid))

    categories = get_categories(page)
    if categories == None:
        raise RuntimeError("Invalid appid")

    return jsonify(categories)
