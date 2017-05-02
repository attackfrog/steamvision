/**
 * Filters lists dynamically, based on user input.
 *
 * Created by Jack McLellan on 5/2/2017 based on work by Kilian Valkhof, source and copyright as follows:
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
        return (a.textContent || a.innerText || "").toUpperCase().indexOf(m[3].toUpperCase())>=0;
    };

    function search_categories(list, input) {
        // Add search functionality to the category search input field
        $(input)
            // When new input is entered,
            .change(function () {
                var query = $(this).val();
                // If user has entered a query,
                if (query) {
                    // Find and show links that contain the query, and hide ones that don't
                    $(list).find("a:not(:Contains(" + query + "))").hide();
                    $(list).find("a:Contains(" + query + ")").show();
                }
                // If the search field is blank, show all links
                else {
                    $(list).find("a").show();
                }
            })
            // Also filter list after each character is entered
            .keyup(function () {
                $(this).change();
            });
    }
    
    function search_games(list, input) {
        // Add search functionality to the games search field
        $(input)
            // When new input is entered,
            .change(function () {
                var query = $(this).val();
                // If user has entered a query,
                if (query) {
                    // Find and show game divs whose titles contain the query, and hide ones that don't
                    $(list).find("a:not(:Contains(" + query + "))").parents('.panel').hide();
                    $(list).find("a:Contains(" + query + ")").parents('.panel').show();
                }
                // If the search field is blank, show all games
                else {
                    $(list).find('.panel').show();
                }
            })
            // Also filter list after each character is entered
            .keyup(function () {
                $(this).change();
            })
    }
    // Activate properties when page has loaded
    $(function () {
        search_categories($('#categories'), $('#category-search'));
        search_games($('#accordion'), $('#game-search'));
    })
}(jQuery));
