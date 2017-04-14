import urllib.request
import lxml
from bs4 import BeautifulSoup


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
        return None

    # Get categories
    categories = get_categories(soup)
    ratings = get_ratings(soup)

    return {
        "categories": categories,
        "ratings": ratings
    }

def get_categories(soup):
    """Scrapes game category information from a parsed Steam Store page."""

    # Get appropriate <div>
    div = soup.find(class_="glance_tags")
    if div is None:
        raise RuntimeError("The Steam Store layout changed! Missing \"glance_tags\"")
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
    """Scrapes game ratings summary information from a parsed Steam Store page."""

    # Get appropriate <div>s
    divs = soup.find_all(class_="game_review_summary")
    if divs is None:
        raise RuntimeError("The Steam Store layout changed! Missing \"game_review_summary\"")

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

    # If none of them had those characteristics, it's because the page only has overall reviews, not recent
    elif len(info) == 0:
        # Get the detailed info from this div instead
        div = soup.find_all(class_="responsive_reviewdesc")
        if div is None:
            raise RuntimeError("The Steam Store layout changed! Missing \"responsive_reviewdesc\"")

        # Construct the same kind of list, making a blank item in place of recent reviews information
        info.append({
            "summary": "",
            "details": ""
        })
        info.append({
            "summary": divs[0].contents[0],
            "details": div[0].contents[0].strip()[2:]
        })

    return info
