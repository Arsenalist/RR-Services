from flask import Flask
app = Flask(__name__)
import requests
import os
from flask import jsonify
from flask_cors import CORS
from bs4 import BeautifulSoup
from urllib.parse import urlparse
import redis
import hashlib
import json
from flask import render_template
import jinja2

CORS(app)

my_loader = jinja2.ChoiceLoader([
        app.jinja_loader,
        jinja2.FileSystemLoader(['./templates']),
    ])
app.jinja_loader = my_loader

redis_client = r = redis.from_url(os.environ.get("REDIS_URL"))

def makeRequest(endpoint):
    try:
        r = requests.get(endpoint)
    except requests.exceptions.RequestException as e:
        print ("Could not complete request " + endpoint)
        print (e)
    return r.text

def get_from_general_cache(key):
    return redis_client.get(key)

def store_in_general_cache(key, result, timeout):
    redis_client.set(key, result)
    redis_client.expire(key, timeout)


def considerCache(endpoint, timeout=600):
    key = hashlib.md5(endpoint.encode()).hexdigest()
    result = get_from_general_cache(key)
    if (result is None):
        result = makeRequest(endpoint)
        store_in_general_cache(key, result, timeout)
    return result

def createBoxScore(event, box_score, player_records):

    # line score
    away_team = event['away_team']
    home_team = event['home_team']
    line_scores_away = box_score['line_scores']['away']
    line_scores_home = box_score['line_scores']['home']
    away_score = box_score['score']['away']['score']
    home_score = box_score['score']['home']['score']

    # player records
    away_records_starters = list(filter(lambda record: record['alignment'] == 'away' and record['started_game'] == True, player_records))
    away_records_bench = list(filter(lambda record: record['alignment'] == 'away' and record['started_game'] == False, player_records))
    home_records_starters = list(filter(lambda record: record['alignment'] == 'home' and record['started_game'] == True, player_records))
    home_records_bench = list(filter(lambda record: record['alignment'] == 'home' and record['started_game'] == False, player_records))

    # team records
    away_team_records = box_score['team_records']['away']
    home_team_records = box_score['team_records']['home']

    # content blocks
    header_content = render_template('header.jinja', away_team=away_team, home_team=home_team, away_score=away_score, home_score=home_score)
    line_score_content = render_template('line_score.jinja', away_team=away_team, home_team=home_team, away_score=away_score, home_score=home_score, line_scores_away=line_scores_away, line_scores_home=line_scores_home)
    away_starter_player_records_content = render_template('player_records.jinja', record_type='STARTERS', player_records=away_records_starters)
    away_bench_player_records_content = render_template('player_records.jinja', record_type='BENCH', player_records=away_records_bench)
    away_team_records_content = render_template('team_records.jinja', team_records=away_team_records)
    home_starter_player_records_content = render_template('player_records.jinja', record_type='STARTERS', player_records=home_records_starters)
    home_bench_player_records_content = render_template('player_records.jinja', record_type='BENCH', player_records=home_records_bench)
    home_team_records_content = render_template('team_records.jinja', team_records=home_team_records)

    return render_template('base.jinja', 
        header_content=header_content, 
        line_score_content=line_score_content, 
        away_starter_player_records_content=away_starter_player_records_content,
        away_bench_player_records_content=away_bench_player_records_content,
        away_team_records_content=away_team_records_content,
        home_starter_player_records_content=home_starter_player_records_content,
        home_bench_player_records_content=home_bench_player_records_content,
        home_team_records_content=home_team_records_content)
        

@app.route("/results")
def results():
    return jsonify(json.loads(considerCache('https://api.thescore.com/nba/teams/5/events/previous?rpp=10')))

@app.route("/box/nba/events/<event_id>")
def box(event_id):
    content = get_from_general_cache(event_id)
    if content is None:
        event = json.loads(considerCache('https://api.thescore.com/nba/events/' + event_id))
        box_score = json.loads(considerCache('https://api.thescore.com' + event['box_score']['api_uri']))
        player_records = json.loads(considerCache('https://api.thescore.com' + event['box_score']['api_uri'] + '/player_records'))
        content = createBoxScore(event, box_score, player_records)
        store_in_general_cache(event_id, content, 3600 * 24 * 7)
    return jsonify({'html': content.decode('utf-8')})

@app.route("/schedule")
def schedule():
    return jsonify(json.loads(considerCache('https://api.thescore.com/nba/teams/5/events/upcoming?rpp=-1')))

@app.route("/players")
def players():
    return jsonify(json.loads(considerCache('https://api.thescore.com/nba/teams/5/players')))



@app.route("/players/<player_id>/summary")
def player_summary(player_id):
    return jsonify(json.loads(considerCache('https://api.thescore.com/nba/players/' + player_id + '/summary')))


@app.route("/news")
def injuries():
    text = considerCache('https://www.rotowire.com/basketball/news.php?team=TOR')
    news_updates = []
    soup = BeautifulSoup(text)
    for s in soup.find_all('div', 'news-update'):
        update = {
                'name': s.find('a', 'news-update__player-link').get_text(),
                'headline': s.find('div', 'news-update__headline').get_text(),
                'timestamp': s.find('div', 'news-update__timestamp').get_text(),
                'text': s.find('div', 'news-update__news').get_text()
        }
        news_updates.append(update)
    return jsonify(news_updates)

@app.route("/articles")
def web_articles():
    
    web_articles = json.loads(considerCache(os.environ.get('WEB_ARTICLES_ENDPOINT', '')))
    results = []
    for a in web_articles:
        article = {
                'title': a['description'],
                'href': a['href'],
                'domain': findDomain(a['href'])
        }
        results.append(article)
    return jsonify(results)

@app.route("/salaries")
def salaries():
    
    text = considerCache('https://www.basketball-reference.com/contracts/TOR.html')
    soup = BeautifulSoup(text)

    results = {}

    # get table
    contracts = soup.select('#contracts')
    for c in contracts:
        for a in c.find_all('a'):
                a.parent.append(a.get_text())
                a.decompose()

    if contracts is not None and len(contracts) != 0:
            results['contracts'] = str(contracts[0]).replace('suppress_glossary', 'table table-striped')

    return jsonify(results)

@app.route("/standings")
def standings():
    
    text = considerCache('https://www.basketball-reference.com/leagues/NBA_2019.html')
    soup = BeautifulSoup(text)

    results = {}

    # get table
    east_standings = soup.select('#confs_standings_E')
    if east_standings is not None and len(east_standings) != 0:
            results['east_standings'] = str(east_standings[0]).replace('suppress_all', 'table table-striped')

    west_standings = soup.select('#confs_standings_W')
    if west_standings is not None and len(west_standings) != 0:
            results['west_standings'] = str(west_standings[0]).replace('suppress_all', 'table table-striped')

    return jsonify(results)

def findDomain(url):
    o = urlparse(url)
    return o.hostname

if __name__ == '__main__':
    # Bind to PORT if defined, otherwise default to 5000.
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)   
