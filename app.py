import click

from database import Statistic, PoorlyNamedEmbeddedDocument, FieldAggregates

from datetime import datetime, timedelta
from flask import Flask, jsonify, render_template, request
from flask_mongoengine import MongoEngine
from flask_cache import Cache

app = Flask(__name__)
app.config.from_pyfile('app.cfg')
db = MongoEngine(app)
cache = Cache(app, config={'CACHE_TYPE': 'simple'})

@app.cli.command()
@click.argument('date')
def aggregate(date):
    start = datetime(*map(int, date.split('-')))
    end = start + timedelta(days=1)
    print(start,end)
    for field in Statistic.field_map.values():
        if field in ['d', 't']: continue # skip device_id, submit_time
        res = Statistic.objects().aggregate({ '$match': { 't': { '$gte': start, '$lte': end } } },
                {'$group': { '_id': '$' + field, 'total': { '$sum': 1 }}})
        res2 = list(map(lambda a: PoorlyNamedEmbeddedDocument(v=a['_id'], c=a['total']), res))
        doc = FieldAggregates(d=start, f=field, v=res2)
        doc.save()

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
    return jsonify({
        'result': Statistic.get_most_popular(field, days)
        })

@app.route('/')
@cache.cached(timeout=3600)
def index():
    total = Statistic.get_count(90)
    return render_template('index.html', total=total, len=len,
            devices=Statistic.get_most_popular('model', 90),
            countries=Statistic.get_most_popular('country', 90))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=3000, debug=True)
