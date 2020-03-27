from bs4 import BeautifulSoup
import requests
from pprint import pprint


class DataSource:
    def __init__(self, url):
        self.url = url
        self.data = None
        self.response = None
        self.soup = None

    def fetch(self):
        try:
            self.response = requests.get(self.url)
            self.soup = BeautifulSoup(self.response.text, 'lxml')
        except Exception as e:
            print(f'An Error Occurred: {e}')

    @staticmethod
    def numerify(string: str):
        if '%' in string:
            return float(string[:len(string) - 1])
        elif ',' in string or string.isdigit() or string.startswith('+'):
            return int(string.replace(',', ''))
        else:
            return None

    def get_data(self):
        if self.data is not None:
            return self.data
        else:
            print(f'Data is empty')

    def datafy(self, seq: list):
        pass


class WorldMeter(DataSource):
    url = 'https://www.worldometers.info/coronavirus/'

    def __init__(self):
        super().__init__(self.url)

    def parse(self):
        try:
            tables = self.soup.find(
                'table', id='main_table_countries_today').find_all('tbody')
            t1 = tables[0]
            t1metarows = t1.find_all('tr')
            t1rows = []
            for t in t1metarows:
                t1r = t.find_all('td')
                t1rows.append(t1r)
            self.data = list(map(self.datafy, t1rows))

        except Exception as e:
            print(f'An Error Occurred: {e}')

    def datafy(self, seq: list):
        seq = list(
            map(
                lambda x: x.get_text(strip=True).replace('.', '').replace(
                    ' ', '-'), seq))
        # pprint(seq)
        x = {
            'country': seq[0].lower(),
            'data': {
                'cases': self.numerify(seq[1]),
                'newcases': self.numerify(seq[2]),
                'deaths': self.numerify(seq[3]),
                'newdeaths': self.numerify(seq[4]),
                'recovered': self.numerify(seq[5]),
                'serious': self.numerify(seq[7]),
            }
        }
        return x


if __name__ == "__main__":
    w = WorldMeter()
    w.fetch()
    w.parse()
    d = w.get_data()
    pprint(d)
