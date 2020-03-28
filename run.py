import os
from datetime import datetime
from flask import Flask, jsonify, request
from firebase_admin import credentials, firestore, initialize_app
from source import WorldMeter

# init flask app
app = Flask(__name__)

# init firestore db
cred = credentials.Certificate('key.json')
default_app = initialize_app(cred)
db = firestore.client()

# create collections in firebase
wmtr_ref = db.collection('worldmeter')
bno_ref = db.collection('bno')

# init worldmeter source
wmtr = WorldMeter()


# function to update database
@app.route('/update', methods=['POST'])
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
                return jsonify({'success': True, 'timestamp': timestamp}), 200
            else:
                return jsonify({'success': False}), 401
    except Exception as e:
        return f'An Error Occurred: {e}'


# function to receive country data
@app.route('/data/<string:country>', methods=['GET'])
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


# run flask app
if __name__ == "__main__":
    port = os.environ.get('PORT', 8080)
    app.run(threaded=True, host='0.0.0.0', port=port)
