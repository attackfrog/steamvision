/**
 * Renders the SteamVision lists page.
 *
 * Created by Jack McLellan on 4/29/2017.
 */

$(document).ready(function () {

    // Load information from session storage
    var profile = JSON.parse(sessionStorage.profile);
    var games = JSON.parse(sessionStorage.games);
    var categories = JSON.parse(sessionStorage.categories);
    var account_created = new Date(profile.timecreated * 1000); // convert to milliseconds from seconds

    // Store categories for each game in a window variable
    window.categories_for_game = {};
    for (var i = 0; i < games.length; i++) {
        // If the game loaded properly, with categories,
        if (typeof games[i].categories !== 'undefined') {
            // Add this game's categories as an object property in the form of an array
            window.categories_for_game[games[i].appid] = games[i].categories
        } else {
            // Otherwise, use an empty array
            window.categories_for_game[games[i].appid] = []
        }
    }
    // Store games described by each category in a window variable
    window.games_for_category = {};
    for (var category in categories) {
        // Add a property for this category which will be a set of the games matching that category
        window.games_for_category[category] = [];
        // For each game,
        for (var game in window.categories_for_game) {
            // If the category is in that game's list,
            if (window.categories_for_game[game].indexOf(category) !== -1) {
                // Add it to this category's array
                window.games_for_category[category].push(game);
            }
        }
    }

    // Create objects to hold categories which describe the games in the filtered list and the filtered games
    window.filtered_categories = [];
    window.filtered_games = [];

    // Sort games alphabetically by name
    games = games.sort(function (a, b) {
        return a.name.localeCompare(b.name)
    });

    // Convert the categories object to a list,
    var temp_categories = [];
    for (var category in categories) {
        temp_categories.push([category, categories[category]]);
    }
    // Sort that list alphabetically by category name
    temp_categories = temp_categories.sort(function (a, b) {
        return a[0].localeCompare(b[0])
    });
    // Convert the list back to an object, the properties of which will now be alphabetically sorted
    categories = {};
    for (var i = 0; i < temp_categories.length; i++) {
        categories[temp_categories[i][0]] = temp_categories[i][1]
    }

    // Add user information to nav bar
    var profile_html = '<ul class="nav navbar-nav navbar-right">' +
        '<li>' +
            '<img class="pull-left" style="padding-top: 9px" src="' + profile.avatar + '" />' + // insert avatar here
        '</li>' +
        '<li class="dropdown">' +
            '<a class="dropdown-toggle" data-toggle="dropdown" role="button" aria-haspopup="true" aria-expanded="false">' +
                profile.personaname + ' (' + profile.realname + ')<span class="caret"></span></a>' + // insert names here
            '<ul class="dropdown-menu">' +
                '<li class="dropdown-header">Account since ' +
                    account_created.toLocaleDateString() + '</li>' + // insert account creation date here
                '<li><a href="' + profile.profileurl + '" target="_blank">Community Profile</a></li>' + // insert profile url here
            '</ul>' +
        '</li>' +
        '</ul>';
    $('#navs').append(profile_html);

    // Add categories to categories list
    for (var category in categories) {
        // Skip the blank category
        if (category !== '') {
            var category_html = '<a href="#" class="list-group-item">' +
                '<span class="badge">' + categories[category] + '</span> ' + // insert # of games this category fits
                    category + // insert category name
                '</a>';
            $('#categories').append(category_html);
        }
    }

    // Add games to games list
    for (var i = 0, length = games.length; i < length; i++) {
        var game_html = '<div class="panel panel-default" id="' + games[i].appid + '">' + // id panel with game's appid
                // Header:
                '<div class="panel-heading" role="tab" id="game' + games[i].appid + '">' + // id panel header with game's appid
                    '<h4 class="panel-title">' +
                        '<a role="button" data-toggle="collapse" data-parent="#accordion" href="#collapse' + games[i].appid + '"' + // set collapse toggle ids
                          ' aria-expanded="false" aria-controls="collapse' + games[i].appid + '">' + // set collapse toggle ids
                            games[i].name + // insert game's name
                        '</a>' +
                        '<div class="pull-right sv-quickinfo">';
        // If overall review summary exists, add that info to the title
        if (typeof games[i].ratings !== 'undefined' && games[i].ratings[1].summary !== '') {
            game_html += games[i].ratings[1].summary + ' | '
        }
        // If release date is not unknown, add the year to the title (this assumes the date format ends with a 4-digit year)
        if (typeof games[i].release_date !== 'undefined' && games[i].release_date !== '(Unknown)') {
            game_html += games[i].release_date.slice(-4)
        }
        // Continue with html formatting
            game_html += '</div>' +
                    '</h4>' +
                '</div>' +
                // Body:
                '<div id="collapse' + games[i].appid + '" class="panel-collapse collapse" role="tabpanel" aria-labelledby="game'+ games[i].appid + '">' + // set body's collapse ids
                    '<div class="panel-body">' +
                        '<div class="row">' +
                            '<div class="col-md-4" align="center">' +
                                // Game logo image
                                '<img class="img-responsive" style="margin: auto" ' +
                                     'src="http://media.steampowered.com/steamcommunity/public/images/apps/' + games[i].appid + '/' + games[i].img_logo_url + '.jpg" />' +
                                '<br>';

        // If the game's categories loaded properly,
        if (typeof games[i].categories !== 'undefined') {
            // Loop through and add game's categories
            for (var j = 0, num_cats = games[i].categories.length; j < num_cats; j++) {
                game_html +=    '<span class="label label-info">' + games[i].categories[j] + '</span> '
            }
        }
        // Continue with html formatting
            game_html +=        '</div>' +
                            '<div class="col-md-8">' +
                                '<p>' + games[i].description + '</p>';

        // Add recent ratings if they exist
        if (typeof games[i].ratings !== 'undefined' && games[i].ratings[0].summary !== '') {
            game_html +=        '<p><strong>Recent Reviews: </strong>' + games[i].ratings[0].summary + ' (' + games[i].ratings[0].details + ')</p>'
        }
        // Add overall ratings if they exist
        if (typeof games[i].ratings !== 'undefined' && games[i].ratings[1].summary !== '') {
            game_html +=        '<p class="overall_rating"><strong>Overall Reviews: </strong>' + games[i].ratings[1].summary + ' (' + games[i].ratings[1].details + ')</p>'
        }

        // Add release date if it exists
        if (typeof games[i].release_date !== 'undefined') {
            game_html +=        '<p><strong>Release Date: </strong>' + games[i].release_date + '</p>'
        }

        // and continue with HTML formatting
            game_html +=    '</div>' +
                        '</div>' +
                        '<div class="row">' +
                            '<div class="col-md-12" style="text-align: right">' +
                                // Insert game's appid into links to Store page, community hub, and Steam client game launcher
                                '<a class="btn btn-primary" href="http://store.steampowered.com/app/' + games[i].appid + '/" target="_blank">Store Page</a> ' +
                                '<a class="btn btn-default" href="http://steamcommunity.com/app/' + games[i].appid + '" target="_blank">Community Hub</a> ' +
                                '<a class="btn btn-success" href="steam://run/' + games[i].appid + '">Launch Game</a>' +
                            '</div>' +
                        '</div>' +
                    '</div>' +
                '</div>' +
            '</div> ';

        // Add game to page
        $('#accordion').append(game_html);
    }
});
