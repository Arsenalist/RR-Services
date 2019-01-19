from dataservices import schedule_service, standings_service


def get_briefing():
    next_game = schedule_service.get_next_game()
    previous_game = schedule_service.get_previous_game()
    condensed_standings = standings_service.get_standings_for_briefing()
    result = {
        'next_game': next_game,
        'previous_game': previous_game,
        'standings': condensed_standings
    }
    return result
