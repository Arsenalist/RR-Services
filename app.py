from flask import Flask
app = Flask(__name__)
import requests
from flask import jsonify
from flask_cors import CORS
CORS(app)
@app.route("/results")
def results():
    return jsonify(requests.get('https://api.thescore.com/nba/teams/5/events/upcoming').json())

@app.route("/schedule")
def schedule():
    return jsonify(requests.get('https://api.thescore.com/nba/teams/5/events/upcoming').json())

@app.route("/players")
def players():
    return jsonify(requests.get('https://api.thescore.com/nba/teams/5/players').json())



@app.route("/players/<player_id>/summary")
def player_summary(player_id):
    return jsonify(requests.get('https://api.thescore.com/nba/players/' + player_id + '/summary').json())
