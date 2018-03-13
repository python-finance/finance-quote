"""Wrapper around Quandl API
"""

from . import base


class QuandlQuote(base.Quote):
    QQmap = {}


class QuandlQuoteEURONEXT(QuandlQuote):
    date = None
    open = None
    high = None
    low = None
    last = None
    volume = None
    turnover = None

    def __init__(self, date, open, high, low, last, volume, turnover):
        self.date = base.normalize(date)
        self.open = open
        self.high = high
        self.low = low
        self.last = last
        self.volume = volume
        self.turnover = turnover


QuandlQuote.QQmap['EURONEXT'] = QuandlQuoteEURONEXT


class QuandlQuoteWIKI(QuandlQuote):
    date = None
    open = None
    high = None
    low = None
    close = None
    volume = None
    ex_dividend = None
    split_ratio = None
    adj_open = None
    adj_high = None
    adj_low = None
    adj_close = None
    adj_volume = None

    def __init__(self, date, open, high, low, close, volume, ex_dividend, split_ratio, adj_open, adj_high, adj_low,
                 adj_close, adj_volume):
        self.date = base.normalize(date)
        self.open = open
        self.high = high
        self.low = low
        self.close = close
        self.volume = volume
        self.ex_dividend = ex_dividend
        self.split_ratio = split_ratio
        self.adj_open = adj_open
        self.adj_high = adj_high
        self.adj_low = adj_low
        self.adj_close = adj_close
        self.adj_volume = adj_volume


QuandlQuote.QQmap['WIKI'] = QuandlQuoteWIKI


class QuandlQuoteCURRFX(QuandlQuote):
    date = None
    rate = None
    high_est = None
    low_est = None

    def __init__(self, date, rate, high_est, low_est):
        self.date = base.normalize(date)
        self.rate = rate
        self.high_est = high_est
        self.low_est = low_est


QuandlQuote.QQmap['CURRFX'] = QuandlQuoteCURRFX


def genclass(name, cols):
    """Function to print a new class for a given dataset and given columns"""

    def clean_col(col):
        return (
            col
                .replace("-", "_")
                .replace("(", "")
                .replace(".", "_")
                .replace(")", "")
                .replace(" ", "_")
                .replace("__", "_")
                .lower()
        )

    ncols = list(map(clean_col, cols))
    kls = ["class QuandlQuote{name}(QuandlQuote):".format(name=name)]

    for c in ncols:
        kls.append("    {c} = None".format(c=c))

    kls.append("")
    kls.append("    def __init__(self, {}):".format(",".join(ncols)))

    for c in ncols:
        kls.append("        self.{c} = {c}".format(c=c))
    kls.append("")
    kls.append("QuandlQuote.QQmap['{name}'] = QuandlQuote{name}".format(name=name))

    print("\n".join(kls))


class QuandlSource(base.Source):
    MAX_ATTEMPT = 5

    QUANDL_BASE_URL = "https://www.quandl.com/api/v3/datasets/{symbol}.json"

    def get_historical(self, symbol, date_from, date_to, tz=None):
        try:
            dataset, dataseries = symbol.split("/")
        except:
            raise base.SymbolNotFoundError("Quandl expect a symbol under the form XXX/YYY")

        date_from = base.normalize(date_from)
        date_to = base.normalize(date_to)


        url = self.QUANDL_BASE_URL.format(symbol=symbol)
        self.logger.info("calling {url}".format(url=url))
        resp = self.session.get(url,
                                params={
                                    "start_date": date_from.date().isoformat(),
                                    "end_date": date_to.date().isoformat(),
                                    "order": "asc",
                                })

        resp.raise_for_status()

        info = resp.json()['dataset']

        cols = tuple(info["column_names"])

        try:
            QQ = QuandlQuote.QQmap[dataset]
        except KeyError:
            self.logger.error("dataset not yet supported, please copy this in quandly.py")
            genclass(dataset, cols)
            raise

        return [QQ(*r) for r in info["data"]]
