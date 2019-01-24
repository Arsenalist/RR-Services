import json

from dataservices.utils.httputils import HttpUtils
from dataservices.utils.images import get_team_images


def get_results():
    results = decorate_results(json.loads(
        HttpUtils.make_request('https://api.thescore.com/nba/teams/5/events/previous?rpp=10')))
    return results


def decorate_results(results):
    for r in results:
        if r['away_team']['abbreviation'] == "TOR":
            logos = get_team_images(r['home_team'])
            location = "@"
            opposition = r['home_team']['name']
            if (r['box_score']['score']['away']['score'] > r['box_score']['score']['home']['score']):
                result = "W"
            else:
                result = "L"
        else:
            logos = get_team_images(r['away_team'])
            location = "vs"
            opposition = r['away_team']['name']
            if (r['box_score']['score']['away']['score'] > r['box_score']['score']['home']['score']):
                result = "L"
            else:
                result = "W"
        r['opposition_logos'] = logos
        r['display_string'] = result + ' ' + location + ' ' + opposition
        r['event_id'] = r['api_uri'].split('/')[3]
        r['score_string'] = str(r['box_score']['score']['away']['score']) + '-' + str(r['box_score']['score']['home']['score'])
    return results


def create_box_score(event, box_score, player_records):

    # line score
    away_team = event['away_team']
    home_team = event['home_team']
    line_scores_away = box_score['line_scores']['away']
    line_scores_home = box_score['line_scores']['home']
    away_score = box_score['score']['away']['score']
    home_score = box_score['score']['home']['score']

    # player records
    away_records_starters = list(filter(lambda record: record['alignment'] == 'away' and record['started_game'] == True, player_records))
    away_records_bench = list(filter(lambda record: record['alignment'] == 'away' and record['started_game'] == False and record['dnp_type'] is None, player_records))
    away_records_dnp = list(filter(lambda record: record['alignment'] == 'away' and record['dnp_type'] is not None, player_records))
    home_records_starters = list(filter(lambda record: record['alignment'] == 'home' and record['started_game'] == True, player_records))
    home_records_bench = list(filter(lambda record: record['alignment'] == 'home' and record['started_game'] == False and record['dnp_type'] is None, player_records))
    home_records_dnp = list(filter(lambda record: record['alignment'] == 'home' and record['dnp_type'] is not None, player_records))

    # team records
    away_team_records = box_score['team_records']['away']
    home_team_records = box_score['team_records']['home']

    # logos
    away_team_logos = get_team_images(event['away_team'])
    home_team_logos = get_team_images(event['home_team'])

    return {
        'away_records_starters': away_records_starters,
        'away_records_bench': away_records_bench,
        'away_records_dnp': away_records_dnp,
        'home_records_starters': home_records_starters,
        'home_records_bench': home_records_bench,
        'home_records_dnp': home_records_dnp,
        'home_team_records': [home_team_records],
        'away_team_records': [away_team_records],
        'away_team_name': away_team['name'],
        'home_team_name': home_team['name'] ,
        'away_team_abbreviation': away_team['abbreviation'],
        'home_team_abbreviation': home_team['abbreviation'] ,
        'away_score': away_score,
        'home_score': home_score,
        'line_scores_away': line_scores_away,
        'line_scores_home': line_scores_home,
        'away_team_logos': away_team_logos,
        'home_team_logos': home_team_logos
    }


def create_consolidated_box_score(event_id):
    event = json.loads(HttpUtils.make_request('https://api.thescore.com/nba/events/' + event_id))
    box_score = json.loads(HttpUtils.make_request('https://api.thescore.com' + event['box_score']['api_uri']))
    player_records = json.loads(
        HttpUtils.make_request('https://api.thescore.com' + event['box_score']['api_uri'] + '/player_records'))
    content = create_box_score(event, box_score, player_records)
    return content
