/**
 * Filters the games list by category.
 *
 * Created by Jack McLellan on 5/6/2017.
 */

(function ($) {

    function activate_links(links) {
        $(links).each(function () {
            $(this).click(function () {
                // Get the category's name
                var name = this.innerText.slice(this.innerText.indexOf(' ') + 1);

                // If category is active, deactivate it and remove it from the active categories list
                if ($(this).hasClass('active')) {
                    $(this).removeClass('active');
                    window.active_categories.splice(window.active_categories.indexOf(name), 1);
                }
                // If inactive, activate it and add it to the active categories object
                else {
                    $(this).addClass('active');
                    window.active_categories.push(name);
                }

                // If no categories are selected, show all games and categories
                if (window.active_categories.length === 0) {
                    $('#accordion').children().show();
                    $('#categories').children().show();
                }
                // Iterate through selected categories, creating a list of games described by all of them
                else {
                    window.filtered_games = [];
                    for (var i = 0; i < window.active_categories.length; i++) {
                        // If the list is empty (as when this is the first category),
                        if (window.filtered_games.length === 0) {
                            // Copy this category's games list
                            window.filtered_games = window.games_for_category[window.active_categories[i]].slice()
                        }
                        // If the list is not empty,
                        else {
                            // Iterate through the list of games backwards (removing items will change the index of following items)
                            for (var j = window.filtered_games.length - 1; j >= 0; j--) {
                                // And remove each game that isn't in the current category's list
                                if (window.games_for_category[window.active_categories[i]].indexOf(window.filtered_games[j]) === -1) {
                                    window.filtered_games.splice(j, 1)
                                }
                            }
                        }
                    }
                    // Create object to hold categories which describe the games in the filtered list
                    window.filtered_categories = [];

                    // Hide all games, then show only the ones in the filtered list
                    $('#accordion').children().hide();
                    for (var i = 0; i < window.filtered_games.length; i++) {
                        // Identify the game by its id value
                        $('#' + window.filtered_games[i]).show();

                        // Iterate through each of the categories held by this game and add them to the list
                        for (var j = 0; j < window.categories_for_game[window.filtered_games[i]].length; j++) {
                            // But don't add duplicates of categories already in the list
                            if (window.filtered_categories.indexOf(window.categories_for_game[window.filtered_games[i]][j]) === -1) {
                                window.filtered_categories.push(window.categories_for_game[window.filtered_games[i]][j])
                            }
                        }
                    }
                    // Hide all categories, then show only the ones in the list
                    var category_links = $('#categories');
                    category_links.children().hide();
                    for (var i = 0; i < window.filtered_categories.length; i++) {
                        // Identify them by searching for the category's text
                        category_links.find('a:contains(' + window.filtered_categories[i] + ')').show()
                    }
                }
            })
        })
    }

    // Activate functionality when page has loaded
    $(function () {
        window.active_categories = [];
        activate_links($('#categories').children());

        // Make the function globally accessible so the sorting function can reactivate the category links
        window.activate_links = activate_links();
    })
}(jQuery));
