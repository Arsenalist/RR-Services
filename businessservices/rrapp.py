from cachemanager import cache
from dataservices import results_service, blog_content, standings_service, briefing_service, stats_service, \
    schedule_service


def get_results():
    return cache.consider_cache('results', results_service.get_results)


def get_podcasts(podcast_type):
    return cache.consider_cache('podcasts_' + podcast_type, blog_content.get_podcasts, podcast_type)


def get_web_articles():
    return cache.consider_cache('web_articles', blog_content.get_web_articles)


def get_news():
    return cache.consider_cache('injuries_news', blog_content.get_news)


def get_salaries():
    return cache.consider_cache('salaries', blog_content.get_salaries)


def get_draft_history():
    return cache.consider_cache('draft_history', blog_content.get_draft_history)


def get_latest():
    return cache.consider_cache('latest_content', blog_content.get_latest)


def get_g_league():
    return cache.consider_cache('g_league', blog_content.get_articles_by_category, 2009)


def get_quick_reaction():
    return cache.consider_cache('quick_reaction', blog_content.get_articles_by_category, 1591)


def get_morning_coffee():
    return cache.consider_cache('morning_coffee', blog_content.get_articles_by_category, 978)


def get_columns():
    return cache.consider_cache('columns', blog_content.get_articles_by_category, 1)


def get_raptors_news():
    return cache.consider_cache('raptors_news', blog_content.get_articles_by_category, 2007)


def get_article(hash):
    return cache.consider_cache('article_' + hash, blog_content.get_article, hash)


def get_conference_standings():
    return cache.consider_cache('conference_standings', standings_service.get_conference_standings)


def get_division_standings():
    return cache.consider_cache('division_standings', standings_service.get_division_standings)


def get_league_standings():
    return cache.consider_cache('league_standings', standings_service.get_league_standings)


def get_briefing():
    return cache.consider_cache('briefing', briefing_service.get_briefing)


def get_player_summary_stats():
    return cache.consider_cache('player_summary_stats', stats_service.get_player_summary_stats)


def get_schedule():
    return cache.consider_cache('schedule', schedule_service.get_schedule)


def get_box_score(event_id):
    return cache.consider_cache("box_score_" + event_id, results_service.create_consolidated_box_score, event_id)


def get_players_instagram_feed():
    return cache.consider_cache("players_instagram_feed", blog_content.get_players_instagram_feed)


def get_current_events():
    return cache.consider_cache('current_events', schedule_service.get_current_events)


def get_player_game_log(player_id):
    return cache.consider_cache("player_game_log_" + player_id, stats_service.get_player_game_log, player_id)


def get_youtube_feed():
    return cache.consider_cache("get_youtube_feed", blog_content.get_youtube_feed)
