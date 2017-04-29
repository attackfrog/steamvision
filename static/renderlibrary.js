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
});
