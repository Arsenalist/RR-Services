from flask import Flask
app = Flask(__name__)
import requests
import os
from flask import jsonify
from flask_cors import CORS
from bs4 import BeautifulSoup
from urllib.parse import urlparse


CORS(app)
@app.route("/results")
def results():
    return jsonify(requests.get('https://api.thescore.com/nba/teams/5/events/previous?rpp=10').json())

@app.route("/schedule")
def schedule():
    return jsonify(requests.get('https://api.thescore.com/nba/teams/5/events/upcoming?rpp=-1').json())

@app.route("/players")
def players():
    return jsonify(requests.get('https://api.thescore.com/nba/teams/5/players').json())



@app.route("/players/<player_id>/summary")
def player_summary(player_id):
    return jsonify(requests.get('https://api.thescore.com/nba/players/' + player_id + '/summary').json())


@app.route("/news")
def injuries():
    text = requests.get('https://www.rotowire.com/basketball/news.php?team=TOR').text
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
    
    web_articles = requests.get(os.environ.get('WEB_ARTICLES_ENDPOINT', '')).json()
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
    
    text = requests.get('https://www.basketball-reference.com/contracts/TOR.html').text
    soup = BeautifulSoup(text)

    results = {}

    # get table
    contracts = soup.select('#contracts')
    for c in contracts:
        for a in c.find_all('a'):
                a.parent.append(a.get_text())
                a.decompose()

    if contracts is not None and len(contracts) != 0:
            results['contracts'] = str(contracts[0])

    return jsonify(results)

@app.route("/standings")
def standings():
    
    text = requests.get('https://www.basketball-reference.com/leagues/NBA_2019.html').text
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


    results = []
    for a in web_articles:
        article = {
                'title': a['description'],
                'href': a['href'],
                'domain': findDomain(a['href'])
        }
        results.append(article)
    return jsonify(results)


def findDomain(url):
    o = urlparse(url)
    return o.hostname

if __name__ == '__main__':
    # Bind to PORT if defined, otherwise default to 5000.
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)   
