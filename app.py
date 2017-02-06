import json

from database import Statistic

from datetime import datetime, timedelta
from flask import Flask, jsonify, render_template, request, abort
from flask_mongoengine import MongoEngine
from flask_caching import Cache

app = Flask(__name__)
app.config.from_pyfile('app.cfg')
db = MongoEngine(app)
cache = Cache(app)

with open("countries.json") as f:
    country_map = json.load(f)

def display_thing(thing, column):
    val = thing['_id']
    if column == 'country':
        if val in country_map:
            return country_map[val]
    return val

@app.route('/api/v1/stats', methods=['POST'])
def submit_stats():
    j = request.get_json()
    stat = Statistic(d=j['device_hash'],
            m=j['device_name'], v=j['device_version'],
            u=j['device_country'], c=j['device_carrier'],
            c_id=j['device_carrier_id'])
    stat.save()
    print("Saved")
    return "neat"

@app.route('/api/v1/popular/<string:field>/<int:days>')
@app.route('/api/v1/popular/<int:days>')
@cache.cached(timeout=3600)
def get_devices(field='model', days=90):
    if field == 'device_id':
        return jsonify({'result': 'No!'})
    return jsonify({
        'result': Statistic.get_most_popular(field, days)
        })

@app.route('/')
@cache.cached(timeout=3600)
def index():
    stats = { "model": Statistic.get_most_popular('model', 90), "country": Statistic.get_most_popular("country", 90), "total": Statistic.get_count(90)}
    return render_template('index.html', stats=stats, columns=["model", "country"], display=display_thing)

@app.route('/api/v1/<string:field>/<string:value>')
@cache.cached(timeout=3600)
def api_stats_by_field(field, value):
    '''Get stats by a specific field. Examples:
       /model/hammerhead
       /country/in
       /carrier/T-Mobile
       Each thing returns json blob'''
    return jsonify(Statistic.get_info_by_field(field, value))

@app.route('/<string:field>/<string:value>/')
@cache.cached(timeout=3600)
def stats_by_field(field, value):
    valuemap = { 'model': ['version', 'country'], 'carrier': ['model', 'country'], 'version': ['model', 'country'], 'country': ['model', 'carrier'] }

    if not field in ['model', 'carrier', 'version', 'country'] or not Statistic.has_thing(field, value): 
        abort(404)

    stats = Statistic.get_info_by_field(field, value)
    return render_template("index.html", stats=stats, columns=valuemap[field], value=value, display=display_thing)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=3000, debug=True)
