from conftest import recorder
from finance_quote.yahoo import YahooSource


def test_symbol():
    ys = YahooSource()

    with recorder.use_cassette("yahoo"):
        aapl = ys.get_symbol("AAPL")

    assert aapl.name == "Apple Inc."
    assert aapl.timezone == "EST"
    assert aapl.symbol == "AAPL"


def test_latest():
    ys = YahooSource()

    with recorder.use_cassette("yahoo"):
        aapl = ys.get_latest("AAPL")

    assert aapl.volume > 0
    assert aapl.date.year == 2018
    assert aapl.open == 177.96



def test_historical():
    ys = YahooSource()

    with recorder.use_cassette("yahoo"):
        aapl = ys.get_historical("AAPL")

    assert aapl.volume > 0
    assert aapl.date.year == 2018
    assert aapl.open == 177.96
