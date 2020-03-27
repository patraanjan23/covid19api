import os
import requests
from flask import Flask, request, jsonify
from bs4 import BeautifulSoup
from firebase_admin import credentials, firestore, initialize_app
from source import WorldMeter

# init flask app
app = Flask(__name__)

# init firestore db
cred = credentials.Certificate('key.json')
default_app = initialize_app(cred)
db = firestore.client()
wmtr_ref = db.collection('worldmeter')
wmtr = WorldMeter()
bno_ref = db.collection('bno')

# info for sources
urls = [
    "https://docs.google.com/spreadsheets/u/0/d/e/2PACX-1vR30F8lYP3jG7YOq8es0PBpJIE5yvRVZffOyaqC0GgMBN6yt0Q-NI8pxS7hd1F9dYXnowSC6zpZmW9D/pubhtml/sheet?headers=false&gid=0&range=A1:I193"
]


# functions for use
def is_valid(tds: BeautifulSoup):
    t_class = tds[0]['class']
    if 's15' in t_class or 's21' in t_class:
        return True
    return False


def numerify(string: str):
    if '%' in string:
        return float(string[:len(string) - 1])
    elif ',' in string or string.isdigit():
        return int(string.replace(',', ''))
    else:
        return None


def datafy(country_block):
    x = {
        'country': country_block[0].get_text().lower(),
        'data': {
            'cases': numerify(country_block[1].get_text()),
            'newcases': numerify(country_block[2].get_text()),
            'deaths': numerify(country_block[3].get_text()),
            'newdeaths': numerify(country_block[4].get_text()),
            'deathpercent': numerify(country_block[5].get_text()),
            'serious': numerify(country_block[6].get_text()),
            'recovered': numerify(country_block[7].get_text()),
        }
    }
    return x


@app.route('/update', methods=['POST'])
def update_db():
    try:
        wmtr.fetch()
        wmtr.parse()
        data = wmtr.get_data()
        for d in data:
            country = d['country']
            wmtr_ref.document(country).set(d['data'])
        return jsonify(data), 200
    except Exception as e:
        return f'An Error Occurred: {e}'


# @app.route('/update', methods=['POST'])
def update():
    try:
        res = requests.get(urls[0])
        soup = BeautifulSoup(res.text, 'lxml')
        table = soup.find("tbody")
        rows = table.find_all("tr")
        valid_rows = []
        for r in rows:
            tds = r.find_all("td")
            if is_valid(tds):
                valid_rows.append(tds)
        valid_data = list(map(datafy, valid_rows))
        # api_ref.document(valid_data[0]['country']).set(valid_data[0]['data'])
        # api_ref.document('test').set(valid_data)
        # for data in valid_data:
        #     api_ref.document(data['country']).set(data['data'])
        return jsonify(valid_data), 200
    except Exception as e:
        return f'An Error Occurred: {e}'


@app.route('/data', methods=['GET'])
def send():
    try:
        # return jsonify(wmtr_ref.document('test').get()), 200
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
