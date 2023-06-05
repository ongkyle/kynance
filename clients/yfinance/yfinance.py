from urllib.error import HTTPError
from datetime import date, datetime
import numpy as np
import pandas as pd

import yfinance

class YFinance(object):
    def __init__(self, ticker):
        self.ticker = yfinance.Ticker(ticker=ticker)
    
    def exists(self, ticker=None):
        to_validate = self.ticker
        if ticker:
            to_validate = yfinance.Ticker(ticker=ticker)
        does_exist = True
        try:
            to_validate.info
        except HTTPError as err:
            print(err)
            does_exist = False
        return does_exist
    
    def get_chain_just_after_earnings(self):
        next_earnings_date = self.get_next_earnings_date()
        option_expirations = self.get_option_chain_dates()
        return self.get_closest(needle=next_earnings_date, 
                                haystack=option_expirations)

    def get_option_chain_dates(self):
        as_list = list(self.ticker.options)
        return self.convert_to_dates(as_list)
    
    def get_next_earnings_datetime(self):
        earnings_dates = self.get_earnings_datetimes()
        print(f"get_next_earnings_datetime: {earnings_dates}")
        today = self.today()
        next_earnings_datetime = self.get_closest(today, earnings_dates)
        print(f"get_next_earnings_datetime: {next_earnings_datetime}")
        return next_earnings_datetime
    
    def get_next_earnings_date(self):
        datetime = self.get_next_earnings_datetime()
        datetime = pd.to_datetime(datetime)
        date = datetime.date()
        print(f"get_next_earnings_date: {date}")
        return date

    def get_latest_price(self):
        one_day_history = self.get_one_day_history()
        closing_price = one_day_history["Close"]
        return closing_price[0]

    def get_one_day_history(self):
        return self.get_history(period="1d")

    def get_history(self, period):
        return self.ticker.history(period=period)
    
    def get_earnings_datetimes(self):
        earnings = self.ticker.get_earnings_dates()
        return earnings.index.values
    
    def get_option_chain(self, expiration_date=None, ticker=None):
        to_fetch = self.ticker
        if ticker:
            to_fetch=yfinance.Ticker(ticker=ticker)
        return to_fetch.option_chain(expiration_date)
    
    def get_put_option_chain(self, expiration_date):
        return self.get_option_chain(expiration_date=expiration_date).puts
    
    def get_call_option_chain(self, expiration_date):
        return self.get_option_chain(expiration_date=expiration_date).calls
    
    def get_straddle_price(self, expiration_date, strike):
        call_price = self.get_call_price(expiration_date=expiration_date, strike=strike)
        print (f"get_straddle_price: {call_price}")
        put_price = self.get_put_price(expiration_date=expiration_date, strike=strike)
        print (f"get_straddle_price: {put_price}")
        return sum([call_price, put_price])
        
    def get_call_price(self, expiration_date, strike):
        call_option_chain = self.get_call_option_chain(expiration_date=expiration_date)
        calls_at_strike = call_option_chain[(call_option_chain["strike"].values == strike)]
        return calls_at_strike["lastPrice"][calls_at_strike.index[0]]
    
    def get_put_price(self, expiration_date, strike):
        put_option_chain = self.get_put_option_chain(expiration_date=expiration_date)
        puts_at_strike = put_option_chain[(put_option_chain["strike"].values == strike)]
        print (f"get_put_price: {puts_at_strike}")
        return puts_at_strike["lastPrice"][puts_at_strike.index[0]]

    def get_straddle_predicted_movement(self):
        expiration_date = self.get_chain_just_after_earnings()
        expiration_date = str(expiration_date)
        print(f"get_straddle_predicted_movement: {expiration_date}")
        latest_price = self.get_latest_price()
        option_chain = self.get_option_chain(expiration_date)
        closest_strike_to_latest_price = self.get_closest(latest_price, option_chain.calls["strike"].values)
        straddle_price = self.get_straddle_price(expiration_date=expiration_date, strike=closest_strike_to_latest_price)
        print (f"get_straddle_predicted_movement: {self.ticker.ticker} {straddle_price}")
        straddle_predicted_movement = self.calculate_straddle_predicted_movement(straddle_price, latest_price)
        print (f"get_straddle_predicted_movement: {self.ticker.ticker} {straddle_predicted_movement}")
        straddle_predicted_movement = round(straddle_predicted_movement, 2)
        return straddle_predicted_movement
    
    @staticmethod    
    def today():
        return np.datetime64("today")
    
    @staticmethod
    def get_closest(needle, haystack):
        haystack.sort()
        for potential in haystack:
            if potential >= needle:
                return potential
    
    @staticmethod
    def convert_to_dates(arr):
        return [
            date.fromisoformat(ele) for ele
            in arr
        ]

    @staticmethod
    def calculate_straddle_predicted_movement(straddle_price, latest_price):
        return 100 * (straddle_price / latest_price)