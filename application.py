import os
from flask import Flask, render_template, request, redirect, url_for, g
from flask_jsglue import JSGlue
from http.client import NO_CONTENT


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

    # If no Steam ID was provided just redirect to the home page
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
        return "", NO_CONTENT

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
        return "", NO_CONTENT

    return get_user_profile(request.args.get("id"))


@app.route("/game")
def game():
    """Gets extra information about a Steam game either from its Steam Store page or the local database as JSON."""

    # Make sure an appid was provided
    if not request.args.get("appid"):
        raise RuntimeError("Missing appid")

    return get_game_info(request.args.get("appid"))


@app.route("/library")
def library():
    """Displays user's game library."""

    return render_template("library.html")


@app.route("/error")
def error():
    """Displays an error page with optional error message."""

    if not request.args.get("e"):
        return render_template("error.html")
    else:
        return render_template("error.html", message=request.args.get("e"))


@app.route("/beta")
def index_beta():
    """Beta version of the index"""

    return render_template("index_new.html")


@app.route("/beta/library")
def library_beta():
    """Beta version of the library"""

    return render_template("library_new.html")


@app.route("beta/load")
def load_beta():
    """Beta version of the loading page"""

    return render_template("loading_new.html")


@app.errorhandler(404)
def page_not_found(e):
    """Displays the error page for page not found errors."""

    return render_template("error.html", message=e), 404


@app.errorhandler(500)
def internal_server_error(e):
    """Displays the error page for page not found errors."""

    return render_template("error.html", message=e), 500


@app.teardown_appcontext
def teardown_db(exception):
    """Closes the database connection (if open) when the app shuts down."""

    db = getattr(g, '_database', None)
    if db is not None:
        db.close()
