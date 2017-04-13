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

    if not os.environ.get("API_KEY"):
        raise RuntimeError("API Key not set.")

    vanity = request.args.get("id")

    user_id = urllib.request.urlopen("http://api.steampowered.com/ISteamUser/ResolveVanityURL/v0001/?key={}&vanityurl={}".format(os.environ.get("API_KEY"), vanity))

    user_id = json.load(user_id)

    games_info = urllib.request.urlopen(
        "http://api.steampowered.com/IPlayerService/GetOwnedGames/v0001/?key={}&steamid=76561197960434622&format=json"
        .format(os.environ.get("API_KEY"), user_id["response"]["steamid"]))

    return games_info.read()
