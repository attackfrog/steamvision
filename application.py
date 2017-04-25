import os
from flask import Flask, render_template, request, redirect, url_for, g
from flask_jsglue import JSGlue

from helpers import get_user_games, get_user_profile, get_game_info

# configure application
app = Flask(__name__)
JSGlue(app)


@app.route("/")
def index():
    """Display welcome page."""
    return render_template("index.html")


@app.route("/load")
def load():
    """Displays the loading page, which loads the user's games into browser storage."""

    if not request.args.get("id"):
        return redirect(url_for("index"))

    return render_template("loading.html", id=request.args.get("id"))


@app.route("/user_games")
def user_games():
    """Get a Steam user's list of games from Steam API as JSON."""

    # Make sure (Steam) API key is set, just in case something has gone horribly wrong
    if not os.environ.get("API_KEY"):
        raise RuntimeError("API Key not set.")

    # Make sure an id was provided
    if not request.args.get("id"):
        # If wasn't, return an error value (HTTP "No Content")
        return ('', 204)

    return get_user_games(request.args.get("id"))


@app.route("/user_profile")
def user_profile():
    """Get a Steam user's profile information from Steam API as JSON."""

    # Make sure (Steam) API key is set, just in case something has gone horribly wrong
    if not os.environ.get("API_KEY"):
        raise RuntimeError("API Key not set.")

    # Make sure an id was provided
    if not request.args.get("id"):
        # If wasn't, return an error value (HTTP "No Content")
        return ('', 204)

    return get_user_profile(request.args.get("id"))


@app.route("/game")
def game():
    """Gets extra information about a Steam game either from its Steam Store page or the local database as JSON."""

    # Make sure an appid was provided
    if not request.args.get("appid"):
        raise RuntimeError("Missing appid")

    return get_game_info(request.args.get("appid"))


@app.route("/error")
def error():
    """Displays an error page with optional error message."""

    if not request.args.get("e"):
        return render_template("error.html")
    else:
        return render_template("error.html", message=request.args.get("e"))


@app.teardown_appcontext
def teardown_db(exception):
    """Closes the database connection (if open) when the app shuts down."""

    db = getattr(g, '_database', None)
    if db is not None:
        db.close()
