import robin_stocks.robinhood as rh
import weakref
from robinhood.mixins import *


class Robinhood(OptionsMixin):
    def __init__(self, username=None, password=None, mfa_code=None):
        self.username = username
        self.password = password
        self.mfa_code = mfa_code
        self._finalize = weakref.finalize(self, self.logout)
        self.client = self.login()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self._finalize()

    def login(self):
        rh.login(
            username=self.username,
            password=self.password,
            mfa_code=self.mfa_code
        )
        return rh

    def logout(self):
        try:
            self.client.logout()
        except Exception as _:
            pass

    def filter(self, data, info):
        return self.client.filter_data(data, info)

    def exists(self, ticker):
        name = self.client.get_name_by_symbol(ticker)
        return name != ""

    def get_watchlists_names(self):
        watchlists = self.client.get_all_watchlists("results")
        return [k.get("display_name", None) for k in watchlists]

    def get_watchlists_symbols(self):
        res = dict()
        names = self.get_watchlists_names()
        for name in names:
            items = self.get_watchlist_by_name(name, "results")
            items = self.filter(items, "symbol")
            res[name] = items
        return res

    def get_watchlist_by_name(self, name, info=None):
        return self.client.get_watchlist_by_name(name, info)

    def get_upcoming_earnings_tickers(self):
        return self.client.get_all_stocks_from_market_tag('upcoming-earnings', "symbol")
