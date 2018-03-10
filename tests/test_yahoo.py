import datetime

from conftest import recorder
from finance_quote.yahoo import YahooSource


def test_symbol():
    ys = YahooSource()

    with recorder.use_cassette("yahoo.symbol"):
        aapl = ys.get_symbol("AAPL")

    assert aapl.name == "Apple Inc."
    assert aapl.timezone == "EST"
    assert aapl.symbol == "AAPL"


def test_latest():
    ys = YahooSource()

    with recorder.use_cassette("yahoo.latest"):
        aapl = ys.get_latest("AAPL")

    assert aapl.volume > 0
    assert aapl.date.year == 2018
    assert aapl.open == 177.96



def test_historical():
    ys = YahooSource()

    with recorder.use_cassette("yahoo.historical"):
        aapl = ys.get_historical("AAPL", "2018-01-01", "2018-01-15")

    assert len(aapl) == 9
    assert aapl[0].date == datetime.date(2018, 1, 2)
    assert aapl[-1].date == datetime.date(2018, 1, 12)
