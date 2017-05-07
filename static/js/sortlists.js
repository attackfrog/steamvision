/**
 * Allow user to sort categories and games.
 *
 * Created by Jack McLellan on 5/6/2017.
 */

(function ($) {

    function sort_categories(identifier, type, direction) {
        // When the element is clicked,
        identifier.click(function () {
            var categories = $('#categories');

            // Create an array of the elements of the list
            var sort_list = categories.children().toArray();

            // Sort using the specified method
            switch (type) {
                case 'name':
                    sort_list = sort_categories_by_name(sort_list, direction);
                    break;

                case 'count':
                    sort_list = sort_categories_by_count(sort_list, direction);
                    break;

                default:
                    console.log(type + ' isn\'t a valid thing to sort by...');
            }

            // Replace the old set of elements with the newly sorted set and reactivate sorting functionality
            categories.empty();
            categories.append(sort_list);
            window.activate_links(categories.children());
        })
    }
    
    function sort_categories_by_name(sort_list, direction) {
        if (direction === 'ascending') {
            return sort_list.sort(function (a, b) {
                // Sort the list by comparing the text of the items with the prepended count removed
                return a.innerText.slice(a.innerText.indexOf(' ') + 1).localeCompare(b.innerText.slice(b.innerText.indexOf(' ') + 1))
            })
        }
        else if (direction === 'descending') {
            return sort_list.sort(function (a, b) {
                // Sort the list in the same way, but inverted
                return -(a.innerText.slice(a.innerText.indexOf(' ') + 1).localeCompare(b.innerText.slice(b.innerText.indexOf(' ') + 1)))
            })
        }
        else {
            console.log(direction + ' isn\'t a valid direction to sort a list in.')
        }
    }

    function sort_categories_by_count(sort_list, direction) {
        if (direction === 'ascending') {
            return sort_list.sort(function (a, b) {
                // Sort the list by comparing the values of the prepended counts
                return Number(a.innerText.slice(0, a.innerText.indexOf(' '))) - Number(b.innerText.slice(0, b.innerText.indexOf(' ')))
            })
        }
        else if (direction === 'descending') {
            return sort_list.sort(function (a, b) {
                // Sort the list in the same way, but inverted
                return -(Number(a.innerText.slice(0, a.innerText.indexOf(' '))) - Number(b.innerText.slice(0, b.innerText.indexOf(' '))))
            })
        }
        else {
            console.log(direction + ' isn\'t a valid direction to sort a list in.')
        }
    }

    function sort_games(identifier, type, direction) {
        var games = $('#accordion');

        // When the element is clicked,
        identifier.click(function () {
            // Create an array of the elements of the list
            var sort_list = games.children().toArray();

            // Sort using the specified method
            switch (type) {
                case 'name':
                    sort_list = sort_games_by_name(sort_list, direction);
                    break;

                case 'year':
                    sort_list = sort_games_by_year(sort_list, direction);
                    break;

                case 'rating':
                    sort_list = sort_games_by_rating(sort_list, direction);
                    break;

                default:
                    console.log(type + ' isn\'t a valid thing to sort by...');
            }

            // Replace the old set of elements with the newly sorted set
            games.empty();
            games.append(sort_list);
        })
    }

    function sort_games_by_name(sort_list, direction) {
        if (direction === 'ascending') {
            return sort_list.sort(function (a, b) {
                // Sort the list by comparing the text of the titles of the items
                return $(a).find('.panel-title').text().localeCompare($(b).find('.panel-title').text())
            })
        }
        else if (direction === 'descending') {
            return sort_list.sort(function (a, b) {
                // Sort the list in the same way, but inverted
                return -($(a).find('.panel-title').text().localeCompare($(b).find('.panel-title').text()))
            })
        }
        else {
            console.log(direction + ' isn\'t a valid direction to sort a list in.')
        }
    }

    function sort_games_by_year(sort_list, direction) {
        if (direction === 'ascending') {
            return sort_list.sort(function (a, b) {
                // Try to get the year from the quick info in the game's title
                var year_a = Number($(a).find('.sv-quickinfo').text().slice(-4));
                var year_b = Number($(b).find('.sv-quickinfo').text().slice(-4));

                // If the year was missing, put in dummy value of 3000 so it's sorted last
                if (isNaN(year_a)) {
                    year_a = 3000;
                }
                if (isNaN(year_b)) {
                    year_b = 3000;
                }

                // Sort the list by comparing the release year in the title
                return year_a - year_b
            })
        }
        else if (direction === 'descending') {
            return sort_list.sort(function (a, b) {
                // Try to get the year from the quick info in the game's title
                var year_a = Number($(a).find('.sv-quickinfo').text().slice(-4));
                var year_b = Number($(b).find('.sv-quickinfo').text().slice(-4));

                // If the year was missing, put in dummy value of 0 so it's sorted last
                if (isNaN(year_a)) {
                    year_a = 0;
                }
                if (isNaN(year_b)) {
                    year_b = 0;
                }

                // Sort the list in the same way but inverted
                return -(year_a - year_b)
            })
        }
        else {
            console.log(direction + ' isn\'t a valid direction to sort a list in.')
        }
    }

    function sort_games_by_rating(sort_list, direction) {
        if (direction === 'ascending') {
            return sort_list.sort(function (a, b) {
                // Get the first game's quick info summary and remove the year to get the rating summary
                var rating_a = $(a).find('.sv-quickinfo').text();
                rating_a = rating_a.slice(0, rating_a.indexOf('|') - 1);

                // Do the same for the second game
                var rating_b = $(b).find('.sv-quickinfo').text();
                rating_b = rating_b.slice(0, rating_b.indexOf('|') - 1);

                // Sort the list by comparing the release year in the title
                return convert_rating_to_value(rating_a) - convert_rating_to_value(rating_b)
            })
        }
        else if (direction === 'descending') {
            return sort_list.sort(function (a, b) {
                // Get the first game's quick info summary and remove the year to get the rating summary
                var rating_a = $(a).find('.sv-quickinfo').text();
                rating_a = rating_a.slice(0, rating_a.indexOf('|') - 1);

                // Do the same for the second game
                var rating_b = $(b).find('.sv-quickinfo').text();
                rating_b = rating_b.slice(0, rating_b.indexOf('|') - 1);

                // Sort the list in the same way as ascending but inverted
                return -(convert_rating_to_value(rating_a) - convert_rating_to_value(rating_b))
            })
        }
        else {
            console.log(direction + ' isn\'t a valid direction to sort a list in.')
        }
    }

    function convert_rating_to_value(rating) {
        // For use in a sort function, rank Steam review summaries by positivity/negativity
        switch (rating) {
            case 'Overwhelmingly Positive':
                return 4;

            case 'Very Positive':
                return 3;

            case 'Positive':
                return 2;

            case 'Mostly Positive':
                return 1;

            case 'Mixed':
                return 0;

            case 'Mostly Negative':
                return -1;

            case 'Negative':
                return -2;

            // I'm not sure if the next two summaries exist, but might as well handle them in case they do
            case 'Very Negative':
                return -3;

            case 'Overwhelmingly Negative':
                return -4;

            // If provided some other value, rank it below everything else
            default:
                return -5;
        }
    }

    // Activate sort buttons on page load
    $(function () {
        var category_sort_buttons = $('[aria-label="category-sort"]');
        var game_sort_buttons = $('[aria-label="game-sort"]');

        sort_categories(category_sort_buttons.children('.sv-sort-alpha-asc'), 'name', 'ascending');
        sort_categories(category_sort_buttons.children('.sv-sort-alpha-desc'), 'name', 'descending');
        sort_categories(category_sort_buttons.children('.sv-sort-count-asc'), 'count', 'ascending');
        sort_categories(category_sort_buttons.children('.sv-sort-count-desc'), 'count', 'descending');

        sort_games(game_sort_buttons.children('.sv-sort-alpha-asc'), 'name', 'ascending');
        sort_games(game_sort_buttons.children('.sv-sort-alpha-desc'), 'name', 'descending');
        sort_games(game_sort_buttons.children('.sv-sort-year-asc'), 'year', 'ascending');
        sort_games(game_sort_buttons.children('.sv-sort-year-desc'), 'year', 'descending');
        sort_games(game_sort_buttons.children('.sv-sort-rating-asc'), 'rating', 'ascending');
        sort_games(game_sort_buttons.children('.sv-sort-rating-desc'), 'rating', 'descending');
    })

}(jQuery));
