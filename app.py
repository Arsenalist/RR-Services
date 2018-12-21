from flask import Flask
app = Flask(__name__)
import requests
import os
from flask import jsonify
from flask_cors import CORS
from bs4 import BeautifulSoup
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

if __name__ == '__main__':
    # Bind to PORT if defined, otherwise default to 5000.
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)   
