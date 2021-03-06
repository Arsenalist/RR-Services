import json

from dataservices.utils.httputils import HttpUtils
from dataservices.utils.images import get_player_images


def get_player_summary_stats():
    player_summary_stats = []
    players = json.loads(HttpUtils.make_request('https://api.thescore.com/nba/teams/5/players'))
    for p in players:
        player_summary = json.loads(
            HttpUtils.make_request('https://api.thescore.com/nba/players/' + str(p['id']) + '/summary'))
        player_summary[0]['full_name'] = p['full_name']
        player_summary_stats.append(player_summary[0])
    player_summary_stats.sort(key=lambda x: x['points'], reverse=True)
    return player_summary_stats


def get_player_game_log(player_id):
    player_game_log = []
    player_records = json.loads(HttpUtils.make_request('https://api.thescore.com/basketball/players/'
                                                       + str(player_id) + '/player_records'))

    if len(player_records) == 0:
        raise Exception("No player records found for " + player_id)
    for pr in player_records[0]['player_records']:
        if pr['event']['away_team']['abbreviation'] == "TOR":
            opposition = "@ " + pr['event']['home_team']['abbreviation']
        else:
            opposition = "vs " + pr['event']['away_team']['abbreviation']

        player_game_log.append({
            "game_date": pr['event']['game_date'],
            "opposition": opposition,
            "event_id": pr["event"]["id"],
            "assists": pr["assists"],
            "blocked_shots": pr["blocked_shots"],
            "dnp_details": pr["dnp_details"],
            "dnp_reason": pr["dnp_reason"],
            "dnp_type": pr["dnp_type"],
            "field_goals_attempted": pr["field_goals_attempted"],
            "field_goals_made": pr["field_goals_made"],
            "free_throws_attempted": pr["free_throws_attempted"],
            "free_throws_made": pr["free_throws_made"],
            "minutes": pr["minutes"],
            "personal_fouls": pr["personal_fouls"],
            "plus_minus": pr["plus_minus"],
            "points": pr["points"],
            "rebounds_defensive": pr["rebounds_defensive"],
            "rebounds_offensive": pr["rebounds_offensive"],
            "rebounds_total": pr["rebounds_total"],
            "started_game": pr["started_game"],
            "steals": pr["steals"],
            "three_point_field_goals_attempted": pr["three_point_field_goals_attempted"],
            "three_point_field_goals_made": pr["three_point_field_goals_made"],
            "turnovers": pr["turnovers"]
        })

    return {
        "game_log": player_game_log,
        "player": get_player_info(player_id)
    }


def get_player_info(player_id):
    summary = json.loads(HttpUtils.make_request('https://api.thescore.com/nba/players/'
                                               + str(player_id) + '/summary'))

    if len(summary) == 0:
        raise Exception("Player not found " + player_id)
    print (summary)
    summary = summary[0]
    player = summary["player"]

    return {
        "headshots": get_player_images(player),
        "full_name": player["full_name"],
        "number": player["number"],
        "position": player["position"],
        "season_averages": {
            "minutes_average": summary["minutes_average"],
            "points_average": summary["points_average"],
            "rebounds_total_average": summary["rebounds_total_average"],
            "assists_average": summary["assists_average"],
            "steals_average": summary["steals_average"],
            "blocked_shots_average": summary["blocked_shots_average"],
            "field_goals_percentage": summary["field_goals_percentage"],
            "three_point_field_goals_percentage": summary["three_point_field_goals_percentage"],
            "free_throws_percentage": summary["free_throws_percentage"],
            "turnovers_average": summary["turnovers_average"],
            "games": summary["games"],
            "usage_percentage": summary["usage_percentage"],
        }
    }
