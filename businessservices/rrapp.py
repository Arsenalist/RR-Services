from cachemanager import cache
from dataservices import results_service, blog_content, standings_service, briefing_service, stats_service, \
    schedule_service
import json


def get_results():
    content = cache.get_from_general_cache('results')
    if content is None:
        results = results_service.get_results()
        content = json.dumps(results)
        cache.store_in_general_cache('results', content)
    return content


def get_podcasts():
    content = cache.get_from_general_cache('podcasts')
    if content is None:
        results = blog_content.get_podcasts()
        content = json.dumps(results)
        cache.store_in_general_cache('podcasts', content)
    return content


def get_web_articles():
    content = cache.get_from_general_cache('web_articles')
    if content is None:
        results = blog_content.get_web_articles()
        content = json.dumps(results)
        cache.store_in_general_cache('web_articles', content)
    return content


def get_news():
    content = cache.get_from_general_cache('news')
    if content is None:
        results = blog_content.get_news()
        content = json.dumps(results)
        cache.store_in_general_cache('news', content)
    return content


def get_salaries():
    content = cache.get_from_general_cache('salaries')
    if content is None:
        results = blog_content.get_salaries()
        content = json.dumps(results)
        cache.store_in_general_cache('salaries', content)
    return content


def get_latest():
    content = cache.get_from_general_cache('latest_content')
    if content is None:
        results = blog_content.get_latest()
        content = json.dumps(results)
        cache.store_in_general_cache('latest_content', content)
    return content


def get_article(hash):
    content = cache.get_from_general_cache('article_' + hash)
    if content is None:
        results = blog_content.get_article(hash)
        content = json.dumps(results)
        cache.store_in_general_cache('article_' + hash, content)
    return content


def get_conference_standings():
    content = cache.get_from_general_cache('conference_standings')
    if content is None:
        results = standings_service.get_conference_standings()
        content = json.dumps(results)
        cache.store_in_general_cache('conference_standings', content)
    return content


def get_division_standings():
    content = cache.get_from_general_cache('division_standings')
    if content is None:
        results = standings_service.get_division_standings()
        content = json.dumps(results)
        cache.store_in_general_cache('division_standings', content)
    return content


def get_league_standings():
    content = cache.get_from_general_cache('league_standings')
    if content is None:
        results = standings_service.get_league_standings()
        content = json.dumps(results)
        cache.store_in_general_cache('league_standings', content)
    return content


def get_briefing():
    content = cache.get_from_general_cache('briefing')
    if content is None:
        results = briefing_service.get_briefing()
        content = json.dumps(results)
        cache.store_in_general_cache('briefing', content)
    return content


def get_player_summary_stats():
    content = cache.get_from_general_cache('player_summary_stats')
    if content is None:
        player_summary_stats = stats_service.get_player_summary_stats()
        content = json.dumps(player_summary_stats)
        cache.store_in_general_cache('player_summary_stats', content, 3600 * 24)
    return content


def get_schedule():
    content = cache.get_from_general_cache('schedule')
    if content is None:
        result = schedule_service.get_schedule()
        content = json.dumps(result)
        cache.store_in_general_cache('schedule', content, 3600 * 3)
    return content


def get_box_score(event_id):
    content = cache.get_from_general_cache("box_score_" + event_id)
    if content is None:
        content = results_service.create_consolidated_box_score(event_id)
        content = json.dumps(content)
        cache.store_in_general_cache("box_score_" + event_id, content, 3600 * 24 * 7)
    return content
