/**
 * Filters the games list by category.
 *
 * Created by Jack McLellan on 5/2/2017.
 */

(function ($) {
    /**
    // Filter games by category
    function filter_games(categories) {
        $(categories).each(function () {
            $(this).click(function() {
                // Get the category's name, removing the count from the string
                var name = this.innerText.slice(this.innerText.indexOf(' ') + 1);

                // If the category is active, deactivate it and show all games
                if ($(this).hasClass('active')) {
                    $(this).removeClass('active');
                    $('#accordion').children().show();
                }
                // If the category is inactive, activate it and hide games that don't fit the category
                else {
                    $(this).addClass('active');
                    var accordion = $('#accordion');
                    accordion.children().hide();
                    accordion.find('span:contains(' + name + ')').parents('.panel').show();
                }
            });
        });
    }
     */

    function activate_links(links) {
        $(links).each(function () {
            $(this).click(function () {
                // Get the category's name
                var name = $(this).attr('id');

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
                    $('#accordion').children().show()
                }
                // Iterate through selected categories, creating a list of games described by all of them
                else {
                    var games = [];
                    for (var category in window.active_categories) {
                        // If the list is empty (as when this is the first category), add all that category's games
                        if (games.length === 0) {
                            games = window.games_for_category_arrays[category]
                        }
                        // If the list is not empty, remove all games from it that don't match this category
                        else {
                            for (var i = 0; i < games.length; i++) {
                                if (!window.games_for_category_sets[category].has(games[i])) {
                                    games.splice(i, 1)
                                }
                            }
                        }
                    }
                    // Hide all games, then show only the ones in the filtered list
                    $('#accordion').children().hide()
                    for (var i = 0; i < games.length; i++) {
                        $('#' + games[i]).show()
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
