import lxml
from bs4 import BeautifulSoup


def get_categories(page):
    """Scrapes game category information from a Steam Store page."""

    # Load page into the magical html scraper
    soup = BeautifulSoup(page, "lxml")

    # Make sure the appid was valid and we didn't just get the Steam homepage
    if soup.title.contents[0] == "Welcome to Steam":
        return None

    # Get appropriate <div>
    div = soup.find(class_="glance_tags")
    tag_type = type(div)

    # Create list
    categories = []

    # Extract categories from <div> into list
    for item in div.contents:
        if type(item) == tag_type:
            for navigable_string in item.contents:
                category = str(navigable_string).strip()
                if not category == "+":
                    categories.append(category)

    return categories
