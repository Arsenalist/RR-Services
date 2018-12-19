from flask import Flask
app = Flask(__name__)
import requests
import os
from flask import jsonify
from flask_cors import CORS
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


if __name__ == '__main__':
    # Bind to PORT if defined, otherwise default to 5000.
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)   
