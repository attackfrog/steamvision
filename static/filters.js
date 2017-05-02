/**
 * Filters the games list by category.
 *
 * Created by Jack McLellan on 5/2/2017.
 */

(function ($) {
    // Filter games by category
    function filter_games(category) {
        $(category).click(function () {
            // Get the category's name, removing the count from the string
            var name = $(this).text;
            name.slice(name.indexOf(' ') + 1);

            // If the category is active, deactivate it and show all games
            if ($(category).hasClass('active')) {
                $(category).removeClass('active');
                $('#accordion').children().show();
            }
            // If the category is inactive, activate it and hide games that don't fit the category
            else {
                $(category).addClass('active');
                var accordion = $('#accordion');
                accordion.children().hide();
                accordion.find('span:contains(' + name + ')').parents('.panel').show();
            }
        })
    }
    // Activate functionality when page has loaded
    $(function () {
        // Pass all category list items to the filter function
        filter_games($('#categories').children())
    })
}(jQuery));
