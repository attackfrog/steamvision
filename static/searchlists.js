/**
 * Filters lists dynamically, based on user input.
 *
 * Created by Jack McLellan on 5/6/2017 based on work by Kilian Valkhof, source and copyright as follows:
 * [https://kilianvalkhof.com/2010/javascript/how-to-build-a-fast-simple-list-filter-with-jquery/]
 *
 * Copyright (c) 2010 Kilian Valkhof
 *
 * Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated
 * documentation files (the "Software"), to deal in the Software without restriction, including without limitation the
 * rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to
 * permit persons to whom the Software is furnished to do so, subject to the following conditions:
 *
 * The above copyright notice and this permission notice shall be included in all copies or substantial portions of the
 * Software.
 *
 * THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE
 * WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS
 * OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR
 * OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
 */

(function ($) {
    // custom css expression for a case-insensitive contains()
    jQuery.expr[':'].Contains = function(a,i,m){
        return (a.textContent || a.innerText || "").toUpperCase().indexOf(m[3].toUpperCase()) >= 0;
    };

    // Custom CSS expression for matching category titles exactly
    jQuery.expr[':'].Matches = function(a, i, m) {
        return a.innerText.slice(a.innerText.indexOf(' ') + 1).localeCompare(m) === 0;
    }

    function search_categories(list, input) {
        // Add search functionality to the category search input field
        $(input)
            // When new input is entered,
            .change(function () {
                var query = $(this).val();
                // If user has entered a query,
                if (query) {
                    // Show categories in the filtered list, then hide ones that don't match the query
                    show_filtered_categories(list);
                    $(list).children("a:not(:Contains(" + query + "))").hide();
                }
                // If the search field is blank, show all links
                else {
                    show_filtered_categories(list);
                }
            })
            // Also filter list after each character is entered
            .keyup(function () {
                $(this).change();
            });
    }

    function show_filtered_categories(list) {
        // If there are no active categories, show all categories
        if (window.active_categories.length === 0) {
            $(list).children().show()
        }
        else {
            // Otherwise, hide all categories
            $(list).children().hide();
            // Then iterate through filtered categories list and show categories in it
            for (var i = 0; i < window.filtered_categories.length; i++) {
                // Identify the category by its text
                $(list).children('a:Matches(' + window.filtered_categories[i] + ')').show();
            }
        }
    }
    
    function search_games(list, input) {
        // Add search functionality to the games search field
        $(input)
            // When new input is entered,
            .change(function () {
                var query = $(this).val();
                // If user has entered a query,
                if (query) {
                    // Show games in the current filter
                    show_filtered_games(list);
                    // Search for links that are titles (role='button') which don't contain the query and hide their
                    // parent div panel
                    $(list).find("a[role='button']:not(:Contains(" + query + "))").parents('.panel').hide();
                }
                // If the search field is blank, show all games in the current filter
                else {
                    show_filtered_games(list);
                }
            })
            // Also filter list after each character is entered
            .keyup(function () {
                $(this).change();
            })
    }

    function show_filtered_games(list) {
        // If there are no active categories, show all games
        if (window.active_categories.length === 0) {
            $(list).children().show()
        }
        else {
            // Otherwise, hide all games
            $(list).children().hide();
            // Then iterate through games in filtered list and show games in it
            for (var i = 0; i < window.filtered_games.length; i++) {
                // Identify the game by its id value
                $('#' + window.filtered_games[i]).show();
            }
        }
    }

    // Activate the search fields when the page has loaded
    $(function () {
        search_categories('#categories', '#category-search');
        search_games('#accordion', '#game-search');
    })
}(jQuery));
