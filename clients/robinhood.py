import logging
import random
import weakref
import inspect
from time import sleep
from datetime import date, datetime
from threading import Semaphore

import investpy
import yfinance as yf
import robin_stocks.robinhood as rh
from wrapt_timeout_decorator import *

from clients.yfinance import YFinance
from clients.client import ValidationClient, OptionsClient
from log.mixins import LoggingMixin
from log.metaclass import MethodLoggerMeta

__metaclass__ = MethodLoggerMeta

class RobinhoodBase(object):
    def __init__(self, username=None, password=None, mfa_code=None, concurrency_limit=2, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.username = username
        self.password = password
        self.mfa_code = mfa_code
        self._finalize = weakref.finalize(self, self.logout)
        self.semaphore = Semaphore(concurrency_limit)
        self.login()
    
    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self._finalize()

    def login(self):
        kwargs = {"username": self.username, "password": self.password, "mfa_code": self.mfa_code}
        rh.login(**kwargs)


    def logout(self):
        try:
            rh.logout()
        except Exception as _:
            pass


class RobinhoodValidation(ValidationClient, RobinhoodBase):

    def exists(self, ticker):
        name = rh.get_name_by_symbol(ticker)
        return name != ""

    def supports_options(self, ticker):
        duration = 1 + random.randint(1, 3)
        sleep(duration)
        res = rh.get_chains(symbol=ticker, info="expiration_dates")
        return res


class Robinhood(OptionsClient, RobinhoodBase):

    def filter(self, data, info):
        return rh.filter_data(data, info)

    def exists(self, ticker):
        name = rh.get_name_by_symbol(ticker)
        return name != ""

    def get_watchlists_names(self):
        watchlists = rh.get_all_watchlists("results")
        self.log(watchlists)
        if watchlists:
            return [k.get("display_name", None) for k in watchlists]
        return []

    def get_watchlists_symbols(self):
        res = dict()
        names = self.get_watchlists_names()
        for name in names:
            items = self.get_watchlist_by_name(name, "results")
            items = self.filter(items, "symbol")
            res[name] = items
        return res

    def get_watchlist_by_name(self, name, info=None):
        res = rh.get_watchlist_by_name(name, info)
        self.log(res)
        return res

    def get_upcoming_earnings_tickers(self):
        return rh.get_all_stocks_from_market_tag('upcoming-earnings', "symbol")

    def export_option_trade_history(self, dir_path, file_name=None):
        return rh.export_completed_option_orders(dir_path, file_name)

    def find_options_by_expiration_and_strike(self, symbols, expiration_date, strike_price, info=None):
        with self.semaphore:
            self.login()
            return rh.find_options_by_expiration_and_strike(
                inputSymbols=symbols,
                expirationDate=expiration_date,
                strikePrice=strike_price,
                info=info)

    def find_option_mark_price(self, symbols, expiration_date, strike_price):
        options = self.find_options_by_expiration_and_strike(symbols, expiration_date, strike_price)
        mark_price = []
        if options:
            mark_price = [
                option.get("mark_price", None) for option in options
            ]
        return mark_price

    def find_options_mark_price_by_strike(self, input_symbols, strike_price, option_type=None, info=None):
        with self.semaphore:
            options = rh.find_options_by_strike(input_symbols, strike_price, option_type, info)
            mark_price = []
            if options:
                mark_price = [
                    option.get("mark_price", None) for option in options
                ]
            return mark_price

    def get_earnings_report(self, symbol):
        earnings = rh.get_earnings(symbol=symbol, info="report")
        earnings = [earning for earning in earnings if earning is not None]
        return [report["date"] for report in earnings]

    @staticmethod
    def convert_to_dates(arr):
        return [
            date.fromisoformat(ele) for ele
            in arr
        ]

    @staticmethod
    def get_closest(needle, haystack):
        haystack.sort()
        for potential in haystack:
            if potential >= needle:
                return potential

    def get_next_earnings_date(self, symbol):
        earnings = self.get_earnings_report(symbol)
        earnings_dates = self.convert_to_dates(earnings)
        return self.get_closest(date.today(), earnings_dates)

    def get_options_chain(self, symbol):
        with self.semaphore:
            sleep(1 + random.randint(1, 3))
            res = rh.get_chains(symbol=symbol, info="expiration_dates")
            return res

    def get_option_chain_dates(self, symbol):
        options_chain = self.get_options_chain(symbol)
        if options_chain:
            return self.convert_to_dates(options_chain)
        return []

    def get_chain_just_after_earnings(self, symbol):
        expiration_dates = self.get_option_chain_dates(symbol)
        res = investpy.get_stock_information(stock=symbol, country='united states', as_json=True)
        earnings_date = datetime.strptime(earnings_date, "%d/%m/%Y")
        if date:
            return self.get_closest(earnings_date.date(), expiration_dates)

    def get_latest_price(self, symbol):
        with self.semaphore:
            res = yf.Ticker(symbol)
            price = res.history(period="1d")["Close"][0] 
            return price

    @staticmethod
    def convert_to_float(arr):
        return [
            float(ele) for ele in arr
        ]

    @staticmethod
    def calculate_straddle_predicted_movement(straddle_price, latest_price):
        return 100 * (straddle_price / latest_price)

    # @timeout(10, use_signals=False)
    def get_closest_option_mark_price(self, symbol, expiration_date, latest_price):
        strike_price = latest_price
        option_prices = []
        while len(option_prices) == 0:
            option_prices = self.find_option_mark_price(
                symbol,
                expiration_date=expiration_date,
                strike_price=strike_price,
            )
            strike_price += 0.5
            strike_price = round(strike_price, 1)
        return option_prices

    def get_straddle_predicted_movement(self, symbol):
        post_earnings_expiry_chain = YFinance(symbol).get_chain_just_after_earnings()
        # post_earnings_expiry_chain = self.get_chain_just_after_earnings(symbol)
        if not post_earnings_expiry_chain:
            return
        latest_price = self.get_latest_price(symbol)
        try:
            option_prices = self.get_closest_option_mark_price(symbol, str(post_earnings_expiry_chain), round(latest_price))
        except TimeoutError as err:
            self.log(err, logging.Error)
            return None
        option_prices = self.convert_to_float(option_prices)
        straddle_price = sum(option_prices)
        straddle_predicted_movement = self.calculate_straddle_predicted_movement(straddle_price, latest_price)
        straddle_predicted_movement = round(straddle_predicted_movement, 2)
        return straddle_predicted_movement
