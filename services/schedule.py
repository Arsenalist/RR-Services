import json

from services.utils.misc import considerCache
from services.results import decorate_results
from services.utils.httputils import HttpUtils


def decorate_schedule(schedule):
    result = []
    i = 0
    max_tv_schedules = 10
    for game in schedule:
        if i < max_tv_schedules:
            detail = json.loads(HttpUtils.make_request('https://api.thescore.com' + game['api_uri']))
            game['tv_schedule_display'] = createTvScheduleString(detail)
        else:
            game['tv_schedule_display'] = ""
        i = i + 1
        result.append(game)

        if game['away_team']['abbreviation'] == "TOR":
            game['location'] = "@"
            game['opposition'] = game['home_team']['name']
        else:
            game['location'] = "vs"
            game['opposition'] = game['away_team']['name']

        game['display_string'] = game['location'] + ' ' + game['opposition']
    return result


def get_schedule():
    schedule = json.loads(HttpUtils.make_request('https://api.thescore.com/nba/teams/5/events/upcoming?rpp=-1'))
    result = decorate_schedule(schedule)
    return result


def get_previous_game():
    previous_game = json.loads(considerCache('https://api.thescore.com/nba/teams/5/events/previous?rpp=1'))
    previous_game = decorate_results(previous_game)
    if (len(previous_game) == 0):
        raise Exception("No previous game found")
    previous_game = previous_game[0]
    return previous_game


def get_next_game():
    next_game = json.loads(HttpUtils.make_request('https://api.thescore.com/nba/teams/5/events/upcoming?rpp=1'))
    next_game = decorate_schedule(next_game)
    if len(next_game) != 0:
        next_game = next_game[0]
    else:
        next_game = None
    return next_game


def createTvScheduleString(game):
    tv_listings = []
    if 'tv_listings_by_country_code' in game is not None:
        if 'ca' in game['tv_listings_by_country_code'] is not None:
            tv_listings.extend(game['tv_listings_by_country_code']['ca'])
        if 'us' in game['tv_listings_by_country_code'] is not None:
            tv_listings.extend(game['tv_listings_by_country_code']['us'])
    result = ""
    for tv in tv_listings:
        result += tv['short_name'] + ", "
    if len(result) > 0:
        result = result[:-2]
    return result