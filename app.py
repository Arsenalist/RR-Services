from flask import Flask

from services.blog_content import get_web_articles, get_news, get_salaries
from services.results import get_results, create_consolidated_box_score
from services.schedule import get_schedule, get_previous_game, get_next_game
from services.standings import get_standings_for_briefing, update_cache_with_all_standings
from services.stats import get_player_summary_stats
from services.utils.misc import get_from_general_cache, store_in_general_cache, considerCache, sanitize_content, \
    encode_string, decode_string, get_redis_client

app = Flask(__name__)
import os
from flask import jsonify
from flask_cors import CORS
from bs4 import BeautifulSoup
import json
import jinja2
from services.utils.httputils import HttpUtils

CORS(app)

my_loader = jinja2.ChoiceLoader([
        app.jinja_loader,
        jinja2.FileSystemLoader(['./templates']),
    ])
app.jinja_loader = my_loader

get_redis_client()


@app.route("/results")
def results():
    content = get_from_general_cache('results')
    if content is None:
        results = get_results()
        content = json.dumps(results)
        store_in_general_cache('results', content)

    return jsonResponse(content)


@app.route("/rr/podcasts")
def podcasts():
    return jsonResponse(considerCache('https://assets.raptorsrepublic.com/rapcast.json'))

@app.route("/box/nba/events/<event_id>")
def box(event_id):
    content = get_from_general_cache(event_id)
    if content is None:
        content = create_consolidated_box_score(content, event_id)
        content = json.dumps(content)
        store_in_general_cache(event_id, content, 3600 * 24 * 7)        
    return jsonResponse(content)


@app.route("/schedule")
def schedule():
    content = get_from_general_cache('schedule')    
    if content is None:
        result = get_schedule()
        content = json.dumps(result)
        store_in_general_cache('schedule', content, 3600 * 3)
    return jsonResponse(content)


@app.route("/players/stats")
def players():
    result = get_from_general_cache('player_summary_stats')
    if result is None:
        player_summary_stats = get_player_summary_stats()
        result = json.dumps(player_summary_stats)
        store_in_general_cache('player_summary_stats', result, 3600 * 24)
    return jsonResponse(result)


@app.route("/briefing")
def briefing():
    next_game = get_next_game()

    previous_game = get_previous_game()

    condensed_standings = get_standings_for_briefing()

    return jsonify({
        'next_game': next_game,
        'previous_game': previous_game,
        'standings': condensed_standings
    })


@app.route("/news")
def injuries():
    news_updates = get_news()
    return jsonify(news_updates)


@app.route("/articles")
def web_articles():
    
    results = get_web_articles()
    return jsonify(results)


@app.route("/salaries")
def salaries():
    
    results = get_salaries()

    return jsonify(results)


@app.route("/standings/conference")
def get_conference_standings():
    result = get_from_general_cache('conference_standings')
    if result is None:
        update_cache_with_all_standings()
        result = get_from_general_cache('conference_standings')
    return jsonResponse(result)

@app.route("/standings/division")
def get_division_standings():
    result = get_from_general_cache('division_standings')
    if result is None:
        update_cache_with_all_standings()
        result = get_from_general_cache('division_standings')
    return jsonResponse(result)

@app.route("/standings/league")
def get_league_standings():
    result = get_from_general_cache('league_standings')
    if result is None:
        update_cache_with_all_standings()
        result = get_from_general_cache('league_standings')
    return jsonResponse(result)


@app.route("/rr/content/latest")
def get_main_rr_content():
    soup = BeautifulSoup(HttpUtils.make_request('https://www.raptorsrepublic.com/amp/', with_headers=True))
    items = []
    for item in soup.select('.amp-wp-article-header'):
        items.append({
            'title': item.find('a').get_text(),
            'url': item.find('a')['href'],
            'hash': encode_string(item.find('a')['href']),
            'image': item.find('amp-img')['src'].replace('-100x75', ''),
            'excerpt': item.find('div', class_='amp-wp-content-loop').find('p').get_text()
        })
    return jsonify(items)

@app.route("/rr/content/article/<hash>")
def get_rr_article(hash):    
    url = decode_string(hash)
    soup = BeautifulSoup(HttpUtils.make_request(url, with_headers=True))
    article = {   
        'title': soup.find('h1', class_='amp-wp-title').get_text(),
        'image': soup.find('amp-img', class_='attachment-large')['src'],
        'html': sanitize_content(str(soup.find('div', class_='the_content'))),
        'author': soup.find('span', class_='amp-wp-author').get_text()
    }
    return jsonify(article)


application = app

def jsonResponse(content):
    response = app.response_class(
        response=content,
        status=200,
        mimetype='application/json'
    )
    return response

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    application.run(debug=True, host='0.0.0.0', port=port)


