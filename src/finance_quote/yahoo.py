"""Wrapper around Yahoo Finance API
https://query1.finance.yahoo.com/v7/finance/download/aapl?period1=1487685205&period2=1495457605&interval=1d&events=history&crumb=dU2hYSfAy9E
https://query1.finance.yahoo.com/v7/finance/quote?symbols=TLS.AX,MUS.AX
https://help.yahoo.com/kb/SLN2310.html
"""
import csv
import datetime
import logging
import re
from decimal import Decimal
from time import sleep

import pytz
import requests

from . import base


class YahooSymbol(base.Symbol):
    name = None
    symbol = None
    exchange = None
    timezone = None
    currency = None

    def __init__(self, name, symbol, exchange, timezone, currency):
        self.name = name
        self.symbol = symbol
        self.exchange = exchange
        self.timezone = timezone
        self.currency = currency

    def __repr__(self):
        return "<symbol:{self.name}>".format(self=self)


class YahooQuote(base.Quote):
    date = None
    open = None
    high = None
    low = None
    close = None
    adj_close = None
    volume = None

    def __init__(self, date, open, high, low, close, adj_close, volume):
        self.date = date
        self.open = open
        self.high = high
        self.low = low
        self.close = close
        self.adj_close = adj_close
        self.volume = volume


class YahooSource(base.Source):
    MAX_ATTEMPT = 5

    YAHOO_BASE_URL = "https://query1.finance.yahoo.com/v7/finance"

    def get_symbol(self, symbol):
        resp = self.session.get("{}/quote".format(self.YAHOO_BASE_URL),
                                params={
                                    "symbols": symbol
                                })
        resp.raise_for_status()

        try:
            data = resp.json()['quoteResponse']['result'][0]
        except IndexError:
            raise base.SymbolNotFoundError("Can't find information on symbol '{}' on yahoo".format(symbol))

        tz = pytz.timezone(data['exchangeTimezoneShortName'])

        return YahooSymbol(
            data['longName'],
            data['symbol'],
            data['exchange'],
            data['exchangeTimezoneShortName'],
            data['currency'],
        )

    def get_latest(self, symbol):
        resp = self.session.get("{}/quote".format(self.YAHOO_BASE_URL),
                                params={
                                    "symbols": symbol
                                })
        resp.raise_for_status()

        try:
            data = resp.json()['quoteResponse']['result'][0]
        except IndexError:
            raise base.SymbolNotFoundError("Can't find information on symbol '{}' on yahoo".format(symbol))

        tz = pytz.timezone(data['exchangeTimezoneShortName'])
        print(data)
        return YahooQuote(
            tz.fromutc(datetime.datetime.fromtimestamp(data['regularMarketTime'])),
            data['regularMarketOpen'],
            data['regularMarketDayHigh'],
            data['regularMarketDayLow'],
            data['regularMarketPrice'],
            None,
            data['regularMarketVolume'],
        )

    CRUMBLE_LINK = 'https://finance.yahoo.com/quote/{0}/history?p={0}'
    CRUMBLE_REGEX = r'CrumbStore":{"crumb":"(.*?)"}'
    QUOTE_LINK = 'https://query1.finance.yahoo.com/v7/finance/download/{}?period1={}&period2={}&interval=1d&events=history&crumb={}'

    def get_crumble_and_cookie(self, symbol):
        link = self.CRUMBLE_LINK.format(symbol)
        response = requests.get(link)
        cookie_str = response.headers["set-cookie"]

        match = re.search(self.CRUMBLE_REGEX, response.text)
        crumble_str = match.group(1)
        return crumble_str, cookie_str

    def get_historical(self, symbol, date_from, date_to, tz=None):

        date_from = base.normalize(date_from)
        date_to = base.normalize(date_to)
        time_stamp_from = int(date_from.timestamp())
        time_stamp_to = int(date_to.timestamp())

        for i in range(self.MAX_ATTEMPT):
            logging.info("{} attempt to download quotes for symbol {} from yahoo".format(i, symbol))

            crumble_str, cookie_str = self.get_crumble_and_cookie(symbol)

            link = self.QUOTE_LINK.format(symbol, time_stamp_from, time_stamp_to, crumble_str)

            resp = requests.get(link, headers={'Cookie': cookie_str})
            try:
                resp.raise_for_status()
            except Exception as e:
                sleep(2)
            else:
                break
        else:
            raise e

        csv_data = list(csv.reader(resp.text.strip().split("\n")))

        return [yq
                for data in csv_data[1:]
                for yq in [YahooQuote(datetime.datetime.strptime(data[0], "%Y-%m-%d").date(),
                                      *[Decimal(f) for f in data[1:]])]
                if date_from.date() <= yq.date <= date_to.date()]
