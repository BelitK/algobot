import json
import requests
import csv
from datetime import datetime
from bs4 import BeautifulSoup


class Trader:
    def __init__(self):
        self.url = 'https://coinmarketcap.com/currencies/bitcoin/historical-data/'
        self.jsonFile = 'btc.json'
        self.csvFile = 'btc.csv'
        self.data = []

        if not self.updated_data():
            self.data = self.get_data_from_url()
            with open(self.jsonFile, 'w', encoding='utf-8') as f:
                json.dump(self.data, f, ensure_ascii=False, indent=4)
        else:
            with open(self.jsonFile, 'r', encoding='utf-8') as f:
                self.data = json.load(f)

    def updated_data(self):
        """
        Checks if data in JSON file (if exists) is updated or not.
        :return: boolean of whether file is recent or not
        """
        today = datetime.today().date()
        try:
            with open(self.jsonFile, 'r', encoding='utf-8') as f:
                date = datetime.strptime(json.load(f)[0]['date'], '%b %d, %Y').date()
                return date == today
        except FileNotFoundError:
            return False

    def get_data_from_csv(self):
        with open(self.csvFile) as csv_file:
            csv_reader = csv.reader(csv_file, delimiter=',')
            values = []
            for row in csv_reader:
                values.append({'date': datetime.strptime(row[0], '%m/%d/%y').date(),
                               'open': float(row[1]),
                               'high': float(row[2]),
                               'low': float(row[3]),
                               'close': float(row[4]),
                               'volume': float(row[5]),
                               'marketCap': float(row[6]),
                               })
            return values

    def get_data_from_url(self):
        """
        Scrapes latest BTC values from CoinMarketCap and returns them in a list of dictionaries.
        :return: list of dictionaries
        """
        response = requests.get(self.url)
        soup = BeautifulSoup(response.text, 'html.parser')
        rows = soup.find_all('tr', attrs={'class': 'cmc-table-row'})
        values = []

        for row in rows:
            cols = row.find_all('td')
            values.append({'date': datetime.strptime(cols[0].text, '%b %d, %Y').date(),
                           'open': float(cols[1].text),
                           'high': float(cols[2].text),
                           'low': float(cols[3].text),
                           'close': float(cols[4].text),
                           'volume': float(cols[5].text),
                           'marketCap': float(cols[6].text),
                           })
        return values

    def get_sma(self, days, parameter, shift=0, round_value=True):
        """
        Returns the simple moving average with data provided.
        :param boolean round_value: Boolean that specifies whether return value should be rounded
        :param int days: Number of days for average
        :param int shift: Days shifted from today
        :param str parameter: Parameter to get the average of (e.g. open, close, high or low values)
        :return: SMA
        """
        data = self.data[shift:days + shift]
        sma = sum([float(day[parameter].replace(',', '')) for day in data]) / days
        if round_value:
            return round(sma, 2)
        return sma

    def get_ema(self, sma_days, ema_days, parameter, round_value=True):
        """
        Returns the exponential moving average with data provided.
        :param round_value: Boolean that specifies whether return value should be rounded
        :param int sma_days: SMA days to get first EMA
        :param int ema_days: Days to iterate EMA for
        :param str parameter: Parameter to get the average of (e.g. open, close, high, or low values)
        :return: EMA
        """
        ema = self.get_sma(sma_days, parameter, shift=ema_days, round_value=False)
        for day in range(ema_days):
            multiplier = 2 / (sma_days + day + 1)
            current_index = ema_days - day - 1
            value = float(self.data[current_index][parameter].replace(',', ''))
            ema = value * multiplier + ema * (1 - multiplier)
        if round_value:
            return round(ema, 2)
        return ema

    def __str__(self):
        return f'Trader()'

    def __repr__(self):
        return 'Trader()'
