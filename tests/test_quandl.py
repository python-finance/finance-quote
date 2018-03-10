import datetime

from conftest import recorder
from finance_quote.quandl import QuandlSource


def test_historical():
    ys = QuandlSource()

    with recorder.use_cassette("quandl.historical.wiki"):
        aapl = ys.get_historical("WIKI/AAPL", "2018-01-01", "2018-01-15")

    assert len(aapl) == 9
    assert aapl[0].date == datetime.datetime(2018, 1, 2)
    assert aapl[-1].date == datetime.datetime(2018, 1, 12)


def test_historical_fx():
    ys = QuandlSource()

    with recorder.use_cassette("quandl.historical.fx"):
        aapl = ys.get_historical("CURRFX/EURUSD", "2018-01-01", "2018-01-15")

    assert len(aapl) == 11
    assert aapl[0].date == datetime.datetime(2018, 1, 1)
    assert aapl[-1].date == datetime.datetime(2018, 1, 15)
