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

    // Add user information to nav bar
    var profile_html = '<ul class="nav navbar-nav navbar-right">' +
        '<li>' +
            '<img class="pull-left" style="padding-top: 9px" src="' + profile.avatar + '" />' + // insert avatar here
        '</li>' +
        '<li class="dropdown">' +
            '<a class="dropdown-toggle" data-toggle="dropdown" role="button" aria-haspopup="true" aria-expanded="false">' +
                profile.personaname + ' (' + profile.realname + ')<span class="caret"></span></a>' + // insert names here
            '<ul class="dropdown-menu">' +
                '<li class="dropdown-header">Account since' +
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
                '<span class="badge">' + categories[category] + '</span>' + // insert # of games this category fits
                    category + // insert category name
                '</a>';
            $('#categories').append(category_html);
        }
    }

    // Add games to games list
    for (var game in games) {
        var game_html = '<div class="panel-group" id="accordion" role="tablist" aria-multiselectable="true">' +
                '<div class="panel panel-default">' +
                    // Header:
                    '<div class="panel-heading" role="tab" id="game' + game.appid + '">' + // id div with game's appid
                        '<h4 class="panel-title">' +
                            '<a role="button" data-toggle="collapse" data-parent="#accordion" href="#collapse' + game.appid + '"' + // set collapse toggle ids
                              ' aria-expanded="false" aria-controls="collapse' + game.appid + '">' + // set collapse toggle ids
                                game.name + // insert game's name
                            '</a>' +
                        '</h4>' +
                    '</div>' +
                    // Body:
                    '<div id="collapse' + game.appid + '" class="panel-collapse collapse" role="tabpanel" aria-labelledby="game'+ game.appid + '">' + // set body's collapse ids
                        '<div class="panel-body">' +
                            '<div class="row">' +
                                '<div class="col-md-4">' +
                                    // Game logo image
                                    '<img class="img-responsive" style="margin: auto" ' +
                                         'src="http://media.steampowered.com/steamcommunity/public/images/apps/' + game.appid + '/' + game.img_logo_url + '.jpg" />' +
                                    '<br>';

        // Loop through and add game's categories
        for (var i = 0, length = game.categories.length; i < length; i++) {
            game_html +=            '<span class="label label-default">' + game.categories[i] + '</span>'
        }
        // Continue with html formatting
        game_html +=            '</div>' +
                                '<div class="col-md-8">' +
                                    '<p>' + game.description + '</p>';

        // Add recent ratings if they exist
        if (game.ratings[0].summary !== '') {
            game_html +=            '<p><strong>Recent Reviews: </strong>' + game.ratings[0].summary + ' (' + game.ratings[0].details + ')</p>'
        }
        // Add overall ratings if they exist
        if (game.ratings[1].summary !== '') {
            game_html +=            '<p><strong>Overall Reviews: </strong>' + game.ratings[1].summary + ' (' + game.ratings[1].details + ')</p>'
        }

        // Continue with HTML formatting
        game_html +=            '</div>' +
                            '</div>' +
                            '<div class="row">' +
                                '<div class="col-md-12" style="text-align: right">' +
                                    // Insert game's appid into links
                                    '<a class="btn btn-primary" href="http://store.steampowered.com/app/' + game.appid + '/" target="_blank">Store Page</a>' +
                                    '<a class="btn btn-default" href="http://steamcommunity.com/app/' + game.appid + '" target="_blank">Community Hub</a>' +
                                    '<a class="btn btn-success" href="steam://run/' + game.appid + '">Launch Game</a>' +
                                '</div>' +
                            '</div>' +
                        '</div>' +
                    '</div>' +
                '</div>' +
            '</div>';

        // Add game to page
        $('#games').append(game_html);
    }
});
