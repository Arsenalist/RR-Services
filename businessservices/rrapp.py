from cachemanager import cache
from dataservices import results_service, blog_content, standings_service, briefing_service, stats_service, \
    schedule_service

def get_results():
    return cache.consider_cache('results', results_service.get_results)


def get_podcasts():
    return cache.consider_cache('podcasts', blog_content.get_podcasts)


def get_web_articles():
    return cache.consider_cache('web_articles', blog_content.get_web_articles)


def get_news():
    return cache.consider_cache('news', blog_content.get_news)


def get_salaries():
    return cache.consider_cache('salaries', blog_content.get_salaries)


def get_latest():
    return cache.consider_cache('latest_content', blog_content.get_latest)


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
