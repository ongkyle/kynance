import random
import weakref
from time import sleep
from datetime import date
from threading import Semaphore

import robin_stocks.robinhood as rh
from wrapt_timeout_decorator import *


class Robinhood(object):
    def __init__(self, username=None, password=None, mfa_code=None, concurrency_limit=2):
        self.username = username
        self.password = password
        self.mfa_code = mfa_code
        self._finalize = weakref.finalize(self, self.logout)
        self.client = self.login()
        self.semaphore = Semaphore(concurrency_limit)

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
        print(watchlists)
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
        res = self.client.get_watchlist_by_name(name, info)
        print(res)
        return res

    def get_upcoming_earnings_tickers(self):
        res = self.client.get_all_stocks_from_market_tag('upcoming-earnings', "symbol")
        print(f"get_upcoming_earnings_tickers: {res}")
        return res

    def export_option_trade_history(self, dir_path, file_name=None):
        res = self.client.export_completed_option_orders(dir_path, file_name)
        print(res)
        return res

    def find_options_by_expiration_and_strike(self, symbols, expiration_date, strike_price, info=None):
        with self.semaphore:
            res = self.client.find_options_by_expiration_and_strike(
                inputSymbols=symbols,
                expirationDate=expiration_date,
                strikePrice=strike_price,
                info=info)
            print(f"find_options_by_expiration_and_strike: {res}")
            return res

    def find_option_mark_price(self, symbols, expiration_date, strike_price):
        options = self.find_options_by_expiration_and_strike(symbols, expiration_date, strike_price)
        print(f"find_option_mark_price: {symbols} {options}")
        mark_price = []
        if options:
            mark_price = [
                option.get("mark_price", None) for option in options
            ]
        return mark_price

    def find_options_mark_price_by_strike(self, input_symbols, strike_price, option_type=None, info=None):
        with self.semaphore:
            options = self.client.find_options_by_strike(input_symbols, strike_price, option_type, info)
            print(f"find_options_mark_price_by_strike: {options}")
            mark_price = []
            if options:
                mark_price = [
                    option.get("mark_price", None) for option in options
                ]
            return mark_price

    def get_earnings_report(self, symbol):
        earnings = self.client.get_earnings(symbol=symbol, info="report")
        print(f"get_earnings_report: {earnings}")
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
        print(f"get_next_earnings_date: {earnings}")
        earnings_dates = self.convert_to_dates(earnings)
        print(f"get_next_earnings_date: {earnings_dates}")
        return self.get_closest(date.today(), earnings_dates)

    def get_options_chain(self, symbol):
        with self.semaphore:
            sleep(1 + random.randint(1, 3))
            res = self.client.get_chains(symbol=symbol, info="expiration_dates")
            print(f"get_options_chain: {res}")
            return res

    def get_option_chain_dates(self, symbol):
        options_chain = self.get_options_chain(symbol)
        if options_chain:
            return self.convert_to_dates(options_chain)
        return []

    def get_chain_just_after_earnings(self, symbol):
        expiration_dates = self.get_option_chain_dates(symbol)
        print(f"get_chain_just_after_earnings: {expiration_dates}")
        earnings_date = self.get_next_earnings_date(symbol)
        print(f"get_chain_just_after_earnings: {earnings_date}")
        if earnings_date:
            return self.get_closest(earnings_date, expiration_dates)

    def get_latest_price(self, symbol):
        with self.semaphore:
            res = float(self.client.get_latest_price(inputSymbols=symbol)[0])
            print(f"get_latest_price: {symbol} {res}")
            return res

    @staticmethod
    def convert_to_float(arr):
        return [
            float(ele) for ele in arr
        ]

    @staticmethod
    def calculate_straddle_predicted_movement(straddle_price, latest_price):
        return 100 * (straddle_price / latest_price)

    @timeout(10, use_signals=False)
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
            print(strike_price)
        return option_prices

    def get_straddle_predicted_movement(self, symbol):
        post_earnings_expiry_chain = self.get_chain_just_after_earnings(symbol)
        if not post_earnings_expiry_chain:
            return
        latest_price = self.get_latest_price(symbol)
        try:
            option_prices = self.get_closest_option_mark_price(symbol, str(post_earnings_expiry_chain), round(latest_price))
        except TimeoutError as err:
            print (f"{err} | {symbol}")
            return None
        option_prices = self.convert_to_float(option_prices)
        straddle_price = sum(option_prices)
        straddle_predicted_movement = self.calculate_straddle_predicted_movement(straddle_price, latest_price)
        straddle_predicted_movement = round(straddle_predicted_movement, 2)
        return straddle_predicted_movement
