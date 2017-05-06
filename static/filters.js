/**
 * Filters the games list by category.
 *
 * Created by Jack McLellan on 5/2/2017.
 */

(function ($) {

    function activate_links(links) {
        $(links).each(function () {
            $(this).click(function () {
                // Get the category's name
                var name = this.innerText.slice(this.innerText.indexOf(' ') + 1);

                // If category is active, deactivate it and delete it from the active categories object
                if ($(this).hasClass('active')) {
                    $(this).removeClass('active');
                    delete window.active_categories[name];
                }
                // If inactive, activate it and add it to the active categories object
                else {
                    $(this).addClass('active');
                    window.active_categories[name] = 1;
                }

                // If no categories are selected, show all games and categories
                if (Object.entries(window.active_categories).length === 0) {
                    $('#accordion').children().show();
                    $('#categories').children().show();
                }
                // Iterate through selected categories, creating a list of games described by all of them
                else {
                    var games = [];
                    for (var category in window.active_categories) {
                        // If the list is empty (as when this is the first category), add all that category's games
                        if (games.length === 0) {
                            games = window.games_for_category[category]
                        }
                        // If the list is not empty, remove all games from it that don't match this category
                        else {
                            for (var i = 0; i < games.length; i++) {
                                if (window.games_for_category[category].indexOf(games[i]) === -1) {
                                    games.splice(i, 1)
                                }
                            }
                        }
                    }
                    // Create object to hold categories which describe the games in the filtered list
                    var filtered_categories = [];

                    // Hide all games, then show only the ones in the filtered list
                    $('#accordion').children().hide();
                    for (var i = 0; i < games.length; i++) {
                        $('#' + games[i]).show();

                        // Iterate through each of the categories held by this game and add them to the list
                        for (var j = 0; j < window.categories_for_game[games[i]].length; j++) {
                            // But don't add duplicates of categories already in the list
                            if (filtered_categories.indexOf(window.categories_for_game[games[i]][j]) === -1) {
                                filtered_categories.push(window.categories_for_game[games[i]][j])
                            }
                        }
                    }

                    // Hide all categories, then show only the ones in the list
                    var category_links = $('#categories');
                    category_links.children().hide();
                    for (var i = 0; i < filtered_categories.length; i++) {
                        // Identify them by searching for the category's text
                        category_links.find('a:contains(' + filtered_categories[i] + ')').show()
                    }
                }
            })
        })
    }

    // Activate functionality when page has loaded
    $(function () {
        window.active_categories = {};
        activate_links($('#categories').children())
    })
}(jQuery));
