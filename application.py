import os
import urllib
import json

from flask import Flask, jsonify, render_template, request, url_for
from flask_jsglue import JSGlue

# configure application
app = Flask(__name__)
JSGlue(app)

@app.route("/")
def index():
    """Display welcome page."""
    return render_template("index.html")

@app.route("/userinfo")
def userinfo():
    """Get info from Steam API about a steam user."""

    # Make sure (Steam) API key is set, just in case something has gone horribly wrong
    if not os.environ.get("API_KEY"):
        raise RuntimeError("API Key not set.")

    # Put the id in a variable to make it more succinct to access
    id = request.args.get("id")

    # Check whether it's a Steam ID of the format Steam_0:1:12345678
    if id[:6].lower() == "steam_" and id[7:8] == ":" and id[9:10] == ":":
        # If so, convert it to a 64bit SteamID
        user_id = int(id[10:])*2 + int(0x0110000100000000) + int(id[8:9])
    # If it isn't, check if it's a vanity URL
    else:
        user_id_info = json.load(urllib.request.urlopen(
            "http://api.steampowered.com/ISteamUser/ResolveVanityURL/v0001/?key={}&vanityurl={}"
            .format(os.environ.get("API_KEY"), id)))
        # If it is, we've got the SteamID
        if user_id_info["response"]["success"] == 1:
            user_id = user_id_info["response"]["steamid"]
        # If it isn't, hopefully they gave us a 64bit SteamID
        else:
            user_id = id

    # Try accessing the user's games list
    try:
        games_info = json.load(urllib.request.urlopen("http://api.steampowered.com/IPlayerService/GetOwnedGames/v0001/?key={}&steamid={}&format=json"
                                            .format(os.environ.get("API_KEY"), user_id)))
    # If it didn't work, give an error.
    except:
        message = "That doesn't seem to be a valid Steam ID."
        return render_template("error.html", message=message)

    if games_info["response"]["game_count"] == 0:
        message = "That account doesn't have any games!"
        return render_template("error.html", message=message)

    return games_info
