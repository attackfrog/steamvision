import os
from flask import Flask, jsonify, render_template, request, url_for
from flask_jsglue import JSGlue

from helpers import get_user_info, get_game_info

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

    return get_user_info(request.args.get("id"))


@app.route("/addgame")
def addgame():
    """Adds information about a game by Steam appid to the database."""

    # Make sure an appid was provided
    if not request.args.get("appid"):
        raise RuntimeError("Missing appid")

    return get_game_info(request.args.get("appid"))
