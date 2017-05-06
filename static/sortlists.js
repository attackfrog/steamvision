/**
 * Allow user to sort categories and games.
 *
 * Created by Jack McLellan on 5/6/2017.
 */

(function ($) {

    function sort_categories(identifier, list, type, direction) {
        // When the element is clicked,
        identifier.onclick(function () {
            // Create an array of the elements of the list
            var sort_list = list.children().toArray();

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

            // Replace the old set of elements with the newly sorted set
            list.children().replaceWith(sort_list);
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

    function sort_games(identifier, list, type, direction) {
        // When the element is clicked,
        identifier.onclick(function () {
            // Create an array of the elements of the list
            var sort_list = list.children().toArray();

            // Sort using the specified method
            switch (type) {
                case 'name':
                    sort_list = sort_games_by_name(sort_list, direction);
                    break;
                default:
                    console.log(type + ' isn\'t a valid thing to sort by...');
            }

            // Replace the old set of elements with the newly sorted set
            list.children().replaceWith(sort_list);
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

    $(function () {
        var category_sort_buttons = $('[aria-label="category-sort"]');
        var game_sort_buttons = $('[aria-label="game-sort"]');
        var categories = $('#categories');
        var games = $('#accordion');

        sort_categories(category_sort_buttons.children('.sv-sort-alpha-asc'), categories, 'name', 'ascending');
        sort_categories(category_sort_buttons.children('.sv-sort-alpha-desc'), categories, 'name', 'descending');
        sort_categories(category_sort_buttons.children('.sv-sort-count-asc'), categories, 'count', 'ascending');
        sort_categories(category_sort_buttons.children('.sv-sort-count-desc'), categories, 'count', 'descending');

        sort_games(game_sort_buttons.children('.sv-sort-alpha-asc'), games, 'name', 'ascending');
        sort_games(game_sort_buttons.children('.sv-sort-alpha-desc'), games, 'name', 'descending');
    })

}(jQuery));
