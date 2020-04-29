# import wget
import os
import csv
import json
import requests
from datetime import datetime


def download_file(url):
    local_filename = url.split('/')[-1]
    # NOTE the stream=True parameter below
    with requests.get(url, stream=True) as r:
        r.raise_for_status()
        with open(local_filename, 'wb') as f:
            for chunk in r.iter_content(chunk_size=12000):
                if chunk:  # filter out keep-alive new chunks
                    f.write(chunk)
                    # f.flush()
    return local_filename


class Timeseries:
    url_confirmed = "https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_confirmed_global.csv"
    url_recovered = "https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_recovered_global.csv"
    url_deaths = "https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_deaths_global.csv"
    file_confirmed = 'time_series_covid19_confirmed_global.csv'
    file_deaths = 'time_series_covid19_deaths_global.csv'
    file_recovered = 'time_series_covid19_recovered_global.csv'
    tsfile = 'timeseries.json'
    data = {
        'confirmed': {},
        'deaths': {},
        'recovered': {},
    }
    data2 = {
        'confirmed': {},
        'deaths': {},
        'recovered': {},
    }

    def __init__(self):
        self.file_confirmed = download_file(self.url_confirmed)
        self.file_deaths = download_file(self.url_deaths)
        self.file_recovered = download_file(self.url_recovered)
        pass

    def fetch_data(self):
        self.__init__()

    @staticmethod
    def convert_data(filename):
        data = []
        with open(filename, newline='') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                data.append(row)
                # print(row)
                # country = row.pop('Country/Region').lower().replace(' ', '')
                # province = row.pop('Province/State').lower().replace(' ', '')
                # lat = row.pop('Lat', None)
                # lon = row.pop('Long', None)
                # newrow = {
                #     'country': country,
                #     'province': province,
                #     'lat': lat,
                #     'long': lon,
                #     'data': row,
                # }
                # data.append(newrow)
        return data

    def parse_data(self):
        self.data['confirmed'] = self.convert_data(self.file_confirmed)
        self.data['recovered'] = self.convert_data(self.file_recovered)
        self.data['deaths'] = self.convert_data(self.file_deaths)
        # self.data['timestamp'] = str(datetime.utcnow())

        # get all countries
        countries = set()

        def organize_data(t):
            for c in self.data[t]:
                countries.add(c['Country/Region'])
            for c in countries:
                provinces = []
                for row in self.data[t]:
                    if c == row['Country/Region']:
                        provinces.append(row)
                self.data2[t][c.lower().replace(' ', '-')] = provinces
        organize_data('confirmed')
        organize_data('recovered')
        organize_data('deaths')
        self.data2['timestamp'] = str(datetime.utcnow())

        # TODO: add way to aggregate for countries with provinces
        # trivial_keys = {'Country/Region', 'Province/State', 'Lat', 'Long'}
        # for c in countries:
        #     aggregate = {}
        #     for row in self.data['confirmed']:
        #         if c == row['Country/Region'] and row['Province/State'] != '':
        #             # provinces.append(row)
        #             for k, v in row.items():
        #                 if k not in trivial_keys:
        #                     if k not in aggregate:
        #                         aggregate[k] = int(v)
        #                     else:
        #                         aggregate[k] += int(v)
        #     self.data2[c] = aggregate

        # TODO: Add file modification check later
        # print(f'modified last at {os.path.getmtime(self.tsfile)}')
        with open(self.tsfile, 'w') as outfile:
            json.dump(self.data2, outfile)
        return self.data2


if __name__ == "__main__":
    ts = Timeseries()
    ts.fetch_data()
    data = ts.parse_data()
    from pprint import pprint
    pprint(data['timestamp'])
    # pprint(data['confirmed']['china'])
    # for c in data['confirmed']:
    #     if c['country'] == 'india':
    #         pprint(c)
