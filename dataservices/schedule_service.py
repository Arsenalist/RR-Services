import json

from dataservices.results_service import decorate_results
from dataservices.utils.httputils import HttpUtils


def decorate_schedule(schedule):
    result = []
    i = 0
    max_tv_schedules = 10
    for game in schedule:
        if i < max_tv_schedules:
            detail = json.loads(HttpUtils.make_request('https://api.thescore.com' + game['api_uri']))
            game['tv_schedule_display'] = create_tv_schedule_string(detail)
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
    previous_game = json.loads(HttpUtils.make_request('https://api.thescore.com/nba/teams/5/events/previous?rpp=1'))
    previous_game = decorate_results(previous_game)
    if len(previous_game) == 0:
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


def create_tv_schedule_string(game):
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


def get_current_events():
    current_events = json.loads('[{"api_uri":"/nba/events/135299","event_status":"in_progress","game_date":"Tue, 22 Jan 2019 01:00:00 -0000","game_type":"Regular Season","id":135299,"status":"in_progress","summary":"NBA - HOU @ PHI PHI 103-76","preview":"/articles/4184178","has_play_by_play_records":true,"tba":false,"subscribable_alerts":[{"key":"game_start","display":"Game Start","default":true},{"key":"game_end","display":"Game End","default":true},{"key":"tight_game","display":"Close Game","default":true},{"key":"mid_quarter","display":"Score - Mid-Quarter","default":false},{"key":"segment_end","display":"Score - End of Quarter","default":true},{"key":"buzzer_beater","display":"Game Winning Buzzer Beater","default":true},{"key":"mid_game_start","display":"Start of Half","default":false}],"league":{"api_uri":"/nba","localizations":{},"resource_uri":"/basketball/leagues/2","daily_rollover_offset":28800.0,"daily_rollover_time":"13:00:00 +0000","default_section":"events","full_name":"NBA Basketball","medium_name":"NBA Basketball","season_type":"regular","short_name":"NBA","slug":"nba","sport_name":"basketball","updated_at":"Mon, 21 Jan 2019 10:29:38 -0000"},"resource_uri":"/basketball/events/135299","box_score":{"api_uri":"/nba/box_scores/140029","id":140029,"progress":{"clock_label":"6:38 4th","string":"6:38 4th","status":"in_progress","event_status":"in_progress","segment":4,"segment_string":"4th","segment_description":"4th Quarter","clock":"6:38","overtime":false},"score":{"home":{"score":103},"away":{"score":76},"winning_team":"/nba/teams/4","losing_team":"/nba/teams/22","tie_game":false},"updated_at":"Tue, 22 Jan 2019 03:17:23 -0000","has_statistics":true},"away_team":{"abbreviation":"HOU","colour_1":"E72230","colour_2":"FDB927","division":"Southwest","has_rosters":true,"api_uri":"/nba/teams/22","full_name":"Houston Rockets","name":"Rockets","id":22,"has_injuries":true,"logos":{"large":"https://d1si3tbndbzwz9.cloudfront.net/basketball/team/22/logo.png","small":"https://d1si3tbndbzwz9.cloudfront.net/basketball/team/22/small_logo.png","w72xh72":"https://d1si3tbndbzwz9.cloudfront.net/basketball/team/22/w72xh72_logo.png","tiny":"https://d1si3tbndbzwz9.cloudfront.net/basketball/team/22/tiny_logo.png","facing":null},"medium_name":"Houston","location":"Houston","short_name":"HOU","updated_at":"Tue, 22 Jan 2019 01:16:54 -0000","resource_uri":"/basketball/teams/22","conference":"Western","has_extra_info":true,"rss_url":"https://feeds.thescore.com/basketball/teams/22.rss","standing":{"api_uri":"/nba/standings/11888","streak":"W1","conference":"Western","conference_abbreviation":"Western","conference_seed":5,"conference_ranking":5,"conference_rank":null,"division":"Southwest","division_ranking":1,"division_rank":1,"division_seed":null,"formatted_rank":"5th Western","place":1,"last_ten_games_record":"6-4","short_record":"26-19","short_away_record":"9-12","short_home_record":"17-7"},"subscribable_alerts":[{"key":"breaking_news","display":"Breaking News","default":true},{"key":"social","display":"Social","default":true},{"key":"features","display":"Features","default":true},{"key":"video","display":"Video","default":true},{"key":"game_start","display":"Game Start","default":true},{"key":"game_end","display":"Game End","default":true},{"key":"tight_game","display":"Close Game","default":false},{"key":"segment_end","display":"Score - End of Quarter","default":false},{"key":"mid_quarter","display":"Score - Mid-Quarter","default":false},{"key":"mid_game_start","display":"Start of Half","default":false}],"subscribable_alert_text":"Keep track of this basketball team by adding it to your feed and subscribing to various alerts.","subscription_count":665906,"payroll_url":"https://www.spotrac.com/nba/houston-rockets"},"home_team":{"abbreviation":"PHI","colour_1":"006BB6","colour_2":"ED174C","division":"Atlantic","has_rosters":true,"api_uri":"/nba/teams/4","full_name":"Philadelphia 76ers","name":"76ers","id":4,"has_injuries":true,"logos":{"large":"https://d1si3tbndbzwz9.cloudfront.net/basketball/team/4/logo.png","small":"https://d1si3tbndbzwz9.cloudfront.net/basketball/team/4/small_logo.png","w72xh72":"https://d1si3tbndbzwz9.cloudfront.net/basketball/team/4/w72xh72_logo.png","tiny":"https://d1si3tbndbzwz9.cloudfront.net/basketball/team/4/tiny_logo.png","facing":null},"medium_name":"Philadelphia","location":"Philadelphia","short_name":"PHI","updated_at":"Tue, 22 Jan 2019 01:16:53 -0000","resource_uri":"/basketball/teams/4","conference":"Eastern","has_extra_info":true,"rss_url":"https://feeds.thescore.com/basketball/teams/4.rss","standing":{"api_uri":"/nba/standings/11149","streak":"L1","conference":"Eastern","conference_abbreviation":"Eastern","conference_seed":4,"conference_ranking":4,"conference_rank":null,"division":"Atlantic","division_ranking":2,"division_rank":2,"division_seed":null,"formatted_rank":"4th Eastern","place":2,"last_ten_games_record":"7-3","short_record":"30-17","short_away_record":"11-12","short_home_record":"19-5"},"subscribable_alerts":[{"key":"breaking_news","display":"Breaking News","default":true},{"key":"social","display":"Social","default":true},{"key":"features","display":"Features","default":true},{"key":"video","display":"Video","default":true},{"key":"game_start","display":"Game Start","default":true},{"key":"game_end","display":"Game End","default":true},{"key":"tight_game","display":"Close Game","default":false},{"key":"segment_end","display":"Score - End of Quarter","default":false},{"key":"mid_quarter","display":"Score - Mid-Quarter","default":false},{"key":"mid_game_start","display":"Start of Half","default":false}],"subscribable_alert_text":"Keep track of this basketball team by adding it to your feed and subscribing to various alerts.","subscription_count":443158,"payroll_url":"https://www.spotrac.com/nba/philadelphia-76ers"}}]')
    result = []
    for c in current_events:
        result.append({
            'event_id': c['id'],
            'clock_label': c['box_score']['progress']['clock_label'],
            'away_team': c['away_team']['name'],
            'home_team': c['home_team']['name'],
            'away_score': c['box_score']['score']['away']['score'],
            'home_score': c['box_score']['score']['home']['score']
        })
    return result
    # return json.loads(HttpUtils.make_request('https://api.thescore.com/nba/teams/4/events/current'))