import os
from flask import Flask, request, jsonify
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
        wmtr.fetch()
        wmtr.parse()
        data = wmtr.get_data()
        for d in data:
            country = d['country']
            wmtr_ref.document(country).set(d['data'])
        return jsonify({'success': True}), 200
    except Exception as e:
        return f'An Error Occurred: {e}'


# function to receive country data
@app.route('/data', methods=['GET'])
def send():
    try:
        country = request.args.get('country')
        if country:
            data = wmtr_ref.document(country).get()
            return jsonify(data.to_dict()), 200
        else:
            raise Exception
    except Exception as e:
        return f'An Error Occurred: {e}'


# run flask app
port = os.environ.get('PORT', 5000)
if __name__ == "__main__":
    app.run(threaded=True, host='0.0.0.0', port=port)
