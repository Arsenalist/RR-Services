import os
import jinja2

from flask import Flask
from flask_cors import CORS

from businessservices import rrapp


def create_flask_app():
    global app
    app = Flask(__name__)
    CORS(app)
    custom_template_loader = jinja2.ChoiceLoader([
        app.jinja_loader,
        jinja2.FileSystemLoader(['./templates']),
    ])
    app.jinja_loader = custom_template_loader
    return app


app = create_flask_app()


@app.route("/results")
def results():
    return json_response(rrapp.get_results())


@app.route("/rr/podcasts")
def podcasts():
    return json_response(rrapp.get_podcasts())


@app.route("/box/nba/events/<event_id>")
def box(event_id):
    return json_response(rrapp.get_box_score(event_id))


@app.route("/schedule")
def schedule():
    return json_response(rrapp.get_schedule())


@app.route("/players/stats")
def players():
    return json_response(rrapp.get_player_summary_stats())


@app.route("/briefing")
def briefing():
    return json_response(rrapp.get_briefing())


@app.route("/news")
def injuries():
    return json_response(rrapp.get_news())


@app.route("/articles")
def web_articles():
    return json_response(rrapp.get_web_articles())


@app.route("/salaries")
def salaries():
    return json_response(rrapp.get_salaries())


@app.route("/standings/conference")
def get_conference_standings():
    return json_response(rrapp.get_conference_standings())


@app.route("/standings/division")
def get_division_standings():
    return json_response(rrapp.get_division_standings())


@app.route("/standings/league")
def get_league_standings():
    return json_response(rrapp.get_league_standings())


@app.route("/rr/content/latest")
def get_main_rr_content():
    return json_response(rrapp.get_latest())


@app.route("/rr/content/article/<hash>")
def get_rr_article(hash):
    return json_response(rrapp.get_article(hash))


def json_response(content):
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
