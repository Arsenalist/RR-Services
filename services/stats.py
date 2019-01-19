import json

from services.utils.httputils import HttpUtils


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