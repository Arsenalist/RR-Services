import json

from dataservices.utils.httputils import HttpUtils


def create_brief_standings(standings):
    standings = createConferenceStandings(standings, 'Eastern')
    standings = standings['standings']
    team_index = -1
    for i in range(0, len(standings)):
        if standings[i]["team"]["id"] == 5:
            team_index = i
            break
    # didn't find the team
    if team_index == -1:
        raise Exception("Team not found")
    # get the two closest teams around the Raptors
    # first place
    if team_index == 0:
        start_index = 0
        end_index = 2
    # last place
    elif team_index == len(standings) - 1:
        start_index = len(standings) - 1 - 2
        end_index = len(standings) - 1
    else:
        start_index = team_index - 1
        end_index = team_index + 1
    standings = standings[start_index:end_index + 1]
    condensed_standings = []
    for s in standings:
        condensed_standings.append({
            'name': s['team']['name'],
            'record': s['short_record'],
            'conference_games_back': s['conference_games_back'],
        })
    return condensed_standings

def get_standings():
    return json.loads(HttpUtils.make_request('http://api.thescore.com/nba/standings/'))


def get_standings_for_briefing():
    standings = json.loads(HttpUtils.make_request('http://api.thescore.com/nba/standings/'))
    condensed_standings = create_brief_standings(standings)
    return condensed_standings


def createConferenceStandings(standings, conference):
    filtered = list(filter(lambda record: record['conference'] == conference, standings))
    filtered.sort(key=lambda record: record['conference_rank'])
    return {
        'label': conference,
        'standings': filtered
    }


def createDivisionStandings(standings, division):
    filtered = list(filter(lambda record: record['division'] == division, standings))
    filtered.sort(key=lambda record: record['division_rank'])
    return {
        'label': division,
        'standings': filtered
    }


def createLeagueStandings(standings):
    standings.sort(key=lambda record: record['winning_percentage'], reverse=True)
    return {
        'label': 'League',
        'standings': standings
    }


def get_league_standings():
    standings = get_standings()
    league_standings = [createLeagueStandings(standings)]
    return create_condensed_standings(league_standings)


def get_division_standings():
    standings = get_standings()
    division_standings = [createDivisionStandings(standings, 'Atlantic'),
                          createDivisionStandings(standings, 'Central'),
                          createDivisionStandings(standings, 'Southeast'),
                          createDivisionStandings(standings, 'Northwest'),
                          createDivisionStandings(standings, 'Pacific'),
                          createDivisionStandings(standings, 'Southwest')]
    return create_condensed_standings(division_standings)


def get_conference_standings():
    standings = get_standings()
    conference_standings = [createConferenceStandings(standings, 'Eastern'),
                            createConferenceStandings(standings, 'Western')]
    return create_condensed_standings(conference_standings)


def create_condensed_standings(standings_list):
    result = []
    for sl in standings_list:
        new_standings = []
        for s in sl['standings']:
            new_standings.append({
                'team': s['team']['name'],
                'record': s['short_record'],
                'winning_percentage': s['winning_percentage'],
                'conference_games_back': s['conference_games_back'],
                'games_back': s['games_back'],
                'last_ten_games_record': s['last_ten_games_record']
            })
        result.append({
            'standings': new_standings,
            'label': sl['label']
        })
    return result
