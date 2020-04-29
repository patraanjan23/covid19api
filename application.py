import os
import json
from datetime import datetime
from flask import Flask, jsonify, request
from firebase_admin import credentials, firestore, initialize_app
from source import WorldMeter
from timeseries import Timeseries

# init flask app
application = Flask(__name__)

# init firestore db
cred = credentials.Certificate('key.json')
default_app = initialize_app(cred)
db = firestore.client()

# create collections in firebase
wmtr_ref = db.collection('worldmeter-aws')
bno_ref = db.collection('bno')

# init worldmeter source
wmtr = WorldMeter()

# init timeseries
ts = Timeseries()

# function to update database
@application.route('/update', methods=['POST'])
def update_db():
    try:
        with open('api.key') as infile:
            api_key = infile.readline().replace('\n', '').strip()
            if api_key == request.args.get('x-api-key'):
                wmtr.fetch()
                wmtr.parse()
                timestamp = str(datetime.utcnow())
                data = wmtr.get_data()
                for d in data:
                    country = d['country']
                    cdata = d['data']
                    cdata['timestamp'] = timestamp
                    wmtr_ref.document(country).set(cdata)
                return jsonify({
                    'success': True,
                    'timestamp': timestamp,
                    'data': data
                }), 200
            else:
                return jsonify({'success': False}), 401
    except Exception as e:
        return f'POST: An Error Occurred: {e}'


# function to receive country data
@application.route('/data/<string:country>', methods=['GET'])
def send(country: str):
    try:
        # country = request.args.get('country')
        if country:
            data = wmtr_ref.document(country).get()
            return jsonify(data.to_dict()), 200
        else:
            raise Exception
    except Exception as e:
        return f'An Error Occurred: {e}'

# update timeseries data
@application.route('/api/v1/timeseries/update', methods=['POST'])
def update_timeseries():
    try:
        with open('api.key', newline='') as infile:
            api_key = infile.readline().strip()
            if api_key == request.args.get('x-api-key'):
                # TODO: implement a cleaned data to firestore code for better scaling
                ts.fetch_data()
                data = ts.parse_data()
                return jsonify({
                    'success': True,
                    'timestamp': data['timestamp'],
                    'test-data': data['confirmed']['us'],
                }), 200
            else:
                return jsonify({
                    'success': False,
                    'error': 'invalid api key',
                }), 401
    except Exception as e:
        return f'TimeseriesUpdate: An Error Occurred: {e}'

# endpoint to fetch country data
@application.route('/api/v1/timeseries/<string:country>', methods=['GET'])
def ts_country(country: str):
    try:
        country = country.lower()
        with open('timeseries.json') as infile:
            data = json.load(infile)
            c_data = data['confirmed'][country]
            r_data = data['recovered'][country]
            d_data = data['deaths'][country]
            result = {
                'confirmed': c_data,
                'recovered': r_data,
                'deaths': d_data,
                'timestamp': data['timestamp'],
            }
            return jsonify(result), 200
            # for c in data['confirmed']:
            #     if c['country'] == country and c['province'] == '':
            #         return jsonify(c), 200
        # return f"TimeseriesFetch: country '{country}' not found"
            # timestamp = data['timestamp']
            # cdata = {}
            # rdata = {}
            # ddata = {}
            # for c in data['confirmed']:
            #     if c['country'] == country:
            #         cdata = c
            #         break
            # for r in data['recovered']:
            #     if r['country'] == country:
            #         rdata = r
            #         break
            # for d in data['deaths']:
            #     if d['country'] == country:
            #         ddata = d
            #         break
            # result = {
            #     'timestamp': cdata['timestamp'],
            #     'country': cdata['country'],
            #     'lat': cdata['lat'],
            #     'long': cdata['long'],
            #     'ts_confirmed': cdata['data'],
            #     'ts_recovered': rdata['data'],
            #     'ts_deaths': ddata['data'],
            #     'success': True,
            # }
            # return jsonify(result), 200
    except Exception as e:
        return f'TimeseriesFetch: An Error Occurred {e}', 404
        # return jsonify({
        #     'success': False,
        #     'error': f'{e}',
        # })


# run flask app
if __name__ == "__main__":
    port = os.environ.get('PORT', 8080)
    application.run(debug=True, threaded=True, host='0.0.0.0', port=port)
