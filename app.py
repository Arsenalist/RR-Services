from flask import Flask
app = Flask(__name__)
import requests
import os
from flask import jsonify, request
from flask_cors import CORS
from bs4 import BeautifulSoup
from urllib.parse import urlparse
import redis
import hashlib
import json
from flask import render_template
import jinja2
import base64
from redis import StrictRedis

CORS(app)

my_loader = jinja2.ChoiceLoader([
        app.jinja_loader,
        jinja2.FileSystemLoader(['./templates']),
    ])
app.jinja_loader = my_loader

redis_client = StrictRedis.from_url(os.environ.get("REDIS_URL"), decode_responses=True)

def makeRequest(endpoint, with_headers=False):
    try:
        headers = None 
        if (with_headers):
            # TODO: Send headerse which APIs are expecting
            headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'}
        r = requests.get(endpoint, headers=headers)
        return r.text
    except requests.exceptions.RequestException as e:
        print ("Could not complete request " + endpoint)
        print (e)    

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
        if (key is not None and result is not None):
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
    away_records_bench = list(filter(lambda record: record['alignment'] == 'away' and record['started_game'] == False and record['dnp_type'] is None, player_records))
    away_records_dnp = list(filter(lambda record: record['alignment'] == 'away' and record['dnp_type'] is not None, player_records))
    home_records_starters = list(filter(lambda record: record['alignment'] == 'home' and record['started_game'] == True, player_records))
    home_records_bench = list(filter(lambda record: record['alignment'] == 'home' and record['started_game'] == False and record['dnp_type'] is None, player_records))
    home_records_dnp = list(filter(lambda record: record['alignment'] == 'home' and record['dnp_type'] is not None, player_records))

    # team records
    away_team_records = box_score['team_records']['away']
    home_team_records = box_score['team_records']['home']

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
        'line_scores_home': line_scores_home
    }        

@app.route("/results")
def results():
    return jsonResponse(considerCache('https://api.thescore.com/nba/teams/5/events/previous?rpp=10'))

@app.route("/rr/podcasts")
def podcasts():
    return jsonResponse(considerCache('https://assets.raptorsrepublic.com/rapcast.json'))

@app.route("/box/nba/events/<event_id>")
def box(event_id):
    content = get_from_general_cache(event_id)
    if content is None:
        event = json.loads(considerCache('https://api.thescore.com/nba/events/' + event_id))
        box_score = json.loads(considerCache('https://api.thescore.com' + event['box_score']['api_uri']))
        player_records = json.loads(considerCache('https://api.thescore.com' + event['box_score']['api_uri'] + '/player_records'))
        content = createBoxScore(event, box_score, player_records)
        content = json.dumps(content)
        store_in_general_cache(event_id, content, 3600 * 24 * 7)        
    return jsonResponse(content)
@app.route("/schedule")
def schedule():
    content = get_from_general_cache('schedule')
    max_tv_schedules = 10
    if content is None:
        schedule = json.loads(makeRequest('https://api.thescore.com/nba/teams/5/events/upcoming?rpp=-1'))
        result = []    
        i = 0
        for game in schedule:
            if i < max_tv_schedules:
                detail = json.loads(makeRequest('https://api.thescore.com' + game['api_uri']))
                game['tv_schedule_display'] = createTvScheduleString(detail)
            else:
                game['tv_schedule_display'] = ""            
            i = i + 1
            result.append(game)
        content = json.dumps(result)
        store_in_general_cache('schedule', content, 3600 * 3)
    return jsonResponse(content)

def createTvScheduleString(game):
    tv_listings = []
    if 'tv_listings_by_country_code' in game is not None:
        if 'ca' in game['tv_listings_by_country_code'] is not None:
            tv_listings.extend(game['tv_listings_by_country_code']['ca'])
        if 'us' in game['tv_listings_by_country_code'] is not None:
            tv_listings.extend(game['tv_listings_by_country_code']['us'])
    result = ""
    for tv in tv_listings:
        result += tv['short_name'] + ", "
    if len(result) > 0:
        result = result[:-2]
    return result

@app.route("/players/stats")
def players():
    result = get_from_general_cache('player_summary_stats')
    if result is None:
        player_summary_stats = []
        players = json.loads(makeRequest('https://api.thescore.com/nba/teams/5/players'))
        for p in players:
            player_summary = json.loads(makeRequest('https://api.thescore.com/nba/players/' + str(p['id']) + '/summary'))
            player_summary[0]['full_name'] = p['full_name']
            player_summary_stats.append(player_summary[0])
        player_summary_stats.sort(key=lambda x: x['points'], reverse=True)
        result = json.dumps(player_summary_stats)
        store_in_general_cache('player_summary_stats', result, 3600 * 24)
    return jsonResponse(result)


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
                'description': a['extended'],
                'href': a['href'],
                'domain': findDomain(a['href'])
        }
        results.append(article)
    return jsonify(results)

def remove_attrs(soup):
    for tag in soup.findAll(True): 
        tag.attrs = None
    return soup


def decorate_table_with_material_design(content):
    replacements = [
        {
        'target': 'class="suppress_glossary sortable stats_table"',
        'replacement': 'role="grid" class="mat-table"'
        },
        {
        'target': '<table ',
        'replacement': '<table role="grid" class="mat-table" '
        },
        {
        'target': '<td>',
        'replacement': '<td role="gridcell" class="mat-cell">'
        },
        {
        'target': '<th>',
        'replacement': '<th role="columnheader" class="mat-header-cell">'
        },
        {
        'target': '<tr>',
        'replacement': '<tr role="row" class="mat-row">'
        }
    ]
    for r in replacements:
        content = content.replace(r['target'], r['replacement'])
    return content

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
        results['contracts'] = decorate_table_with_material_design(str(remove_attrs(contracts[0])))

    return jsonify(results)

@app.route("/standings/conference")
def get_conference_standings():
    result = get_from_general_cache('standings_conference')
    if result is None:
        update_cache_with_all_standings()
        result = get_from_general_cache('standings_conference')
    return jsonify({'html': result})

@app.route("/standings/division")
def get_division_standings():
    result = get_from_general_cache('standings_division')
    if result is None:
        update_cache_with_all_standings()
        result = get_from_general_cache('standings_division')
    return jsonify({'html': result})

@app.route("/standings/league")
def get_league_standings():
    result = get_from_general_cache('standings_league')
    if result is None:
        update_cache_with_all_standings()
        result = get_from_general_cache('standings_league')
    return jsonify({'html': result})


def update_cache_with_all_standings():
    standings = json.loads(makeRequest('http://api.thescore.com/nba/standings/'))
    standings_html = {
        'east': createStandingsHtml(createConferenceStandings(standings, 'Eastern'), 'conference', 'Eastern'),
        'west': createStandingsHtml(createConferenceStandings(standings, 'Western'), 'conference', 'Western'),
        'atlantic': createStandingsHtml(createDivisionStandings(standings, 'Atlantic'), 'division', 'Atlantic'),
        'central': createStandingsHtml(createDivisionStandings(standings, 'Central'), 'division', 'Central'),
        'southeast': createStandingsHtml(createDivisionStandings(standings, 'Southeast'), 'division', 'Southeast'),
        'northwest': createStandingsHtml(createDivisionStandings(standings, 'Northwest'), 'division', 'Northwest'),
        'pacific': createStandingsHtml(createDivisionStandings(standings, 'Pacific'), 'division', 'Pacific'),
        'southwest': createStandingsHtml(createDivisionStandings(standings, 'Southwest'), 'division', 'Southwest'),
        'league': createStandingsHtml(createLeagueStandings(standings), 'league', 'League')
    }
    store_in_general_cache('standings_conference', standings_html['east'] + standings_html['west'], 3600*2)
    store_in_general_cache('standings_division', standings_html['atlantic'] + standings_html['central'] + 
            standings_html['southeast'] + standings_html['northwest'] + standings_html['pacific'] + standings_html['southwest'], 3600*2)
    store_in_general_cache('standings_league', standings_html['league'], 3600*2)

def createStandingsHtml(standings, standings_type, standings_label):
    return render_template('standings.jinja', standings=standings, standings_type=standings_type, standings_label=standings_label)

def createConferenceStandings(standings, conference):
    filtered = list(filter(lambda record: record['conference'] == conference, standings))
    filtered.sort(key=lambda record: record['conference_rank'])
    return filtered

def createDivisionStandings(standings, division):
    filtered = list(filter(lambda record: record['division'] == division, standings))
    filtered.sort(key=lambda record: record['division_rank'])
    return filtered

def createLeagueStandings(standings):
    standings.sort(key=lambda record: record['winning_percentage'], reverse=True)
    return standings

def findDomain(url):
    o = urlparse(url)
    return o.hostname

@app.route("/rr/content/latest")
def get_main_rr_content():
    soup = BeautifulSoup(makeRequest('https://www.raptorsrepublic.com/amp/', with_headers=True))
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
    soup = BeautifulSoup(makeRequest(url, with_headers=True))
    article = {   
        'title': soup.find('h1', class_='amp-wp-title').get_text(),
        'image': soup.find('amp-img', class_='attachment-large')['src'],
        'html': sanitize_content(str(soup.find('div', class_='the_content'))),
        'author': soup.find('span', class_='amp-wp-author').get_text()
    }
    return jsonify(article)

def sanitize_content(content):
    return content.replace("<amp-", "<").replace("</amp-", "</")

def encode_string(to_encode):
    return base64.b64encode(to_encode.encode()).decode('utf-8')

def decode_string(to_decode):
    return base64.b64decode(to_decode.encode('utf-8')).decode()

def jsonResponse(content):
    response = app.response_class(
        response=content,
        status=200,
        mimetype='application/json'
    )
    return response
  
application = app

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    application.run(debug=True, host='0.0.0.0', port=port)   
