from urllib.error import HTTPError
from datetime import date
import numpy as np
import pandas as pd
import logging

from clients.client import ValidationClient, OptionsClient
import yfinance

from requests import Session
from requests_cache import CacheMixin, SQLiteCache
from requests_ratelimiter import LimiterMixin, MemoryQueueBucket
from pyrate_limiter import Duration, RequestRate, Limiter

from log.metaclass import MethodLoggerMeta

__metaclass__ = MethodLoggerMeta

class CachedLimiterSession(CacheMixin, LimiterMixin, Session):
    pass

class YFinanceValidation(ValidationClient, object):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def exists(self, ticker) -> bool:
        ticker = yfinance.Ticker(ticker=ticker)
        does_exist = True
        try:
            ticker.info
        except HTTPError as err:
            self.log(err, logging.ERROR)
            does_exist = False
        return does_exist   

    def supports_options(self, ticker) -> bool:
        ticker = yfinance.Ticker(ticker=ticker)
        supports_options = True
        try:
            ticker.option_chain()
        except TypeError as err:
            self.log(err, logging.ERROR)
            supports_options = False 
        return supports_options
    
    def has_future_earnings_dates(self, ticker: str) -> bool:
        ticker = yfinance.Ticker(ticker=ticker)
        earnings_dates = ticker.get_earnings_dates()
        if earnings_dates is not None:
            return not earnings_dates[
                earnings_dates.index.values >= np.datetime64("today")
            ].empty



class YFinance(OptionsClient, object):
    def __init__(self, ticker, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.session = CachedLimiterSession(
                            limiter=Limiter(RequestRate(2, Duration.SECOND*5)),  # max 2 requests per 5 seconds
                            bucket_class=MemoryQueueBucket,
                            backend=SQLiteCache("/home/kyle/workspace/kynance/yfinance.cache"))
        self.ticker = yfinance.Ticker(ticker=ticker, session=self.session)

    def exists(self, ticker=None):
        to_validate = self.ticker
        if ticker:
            to_validate = yfinance.Ticker(ticker=ticker)
        does_exist = True
        try:
            to_validate.info
        except HTTPError as err:
            self.log(err, logging.ERROR)
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
        today = self.today()
        next_earnings_datetime = self.get_closest(today, earnings_dates)
        return next_earnings_datetime
    
    def get_next_earnings_date(self):
        datetime = self.get_next_earnings_datetime()
        datetime = pd.to_datetime(datetime)
        date = datetime.date()
        return date

    def get_latest_price(self):
        one_day_history = self.get_one_day_history()
        closing_price = one_day_history["Close"]
        price = closing_price[0]
        return price

    def get_one_day_history(self):
        return self.get_history(period="1d")

    def get_history(self, period):
        return self.ticker.history(period=period)
    
    def get_earnings_datetimes(self):
        earnings = self.ticker.get_earnings_dates()
        return earnings.index.values
    
    def get_option_chain(self, expiration_date=None):
        return self.ticker.option_chain(expiration_date)
    
    def get_put_option_chain(self, expiration_date):
        return self.get_option_chain(expiration_date=expiration_date).puts
    
    def get_call_option_chain(self, expiration_date):
        return self.get_option_chain(expiration_date=expiration_date).calls
    
    def get_straddle_price(self, expiration_date, strike):
        call_price = self.get_call_price(expiration_date=expiration_date, strike=strike)
        put_price = self.get_put_price(expiration_date=expiration_date, strike=strike)
        return sum([call_price, put_price])
        
    def get_call_price(self, expiration_date, strike):
        call_option_chain = self.get_call_option_chain(expiration_date=expiration_date)
        calls_at_strike = call_option_chain[(call_option_chain["strike"].values == strike)]
        price = calls_at_strike["lastPrice"][calls_at_strike.index[0]]
        return price
    
    def get_put_price(self, expiration_date, strike):
        put_option_chain = self.get_put_option_chain(expiration_date=expiration_date)
        puts_at_strike = put_option_chain[(put_option_chain["strike"].values == strike)]
        price = puts_at_strike["lastPrice"][puts_at_strike.index[0]]
        return price

    def get_straddle_predicted_movement(self) -> float:
        expiration_date = self.get_chain_just_after_earnings()
        expiration_date = str(expiration_date)
        latest_price = self.get_latest_price()
        option_chain = self.get_option_chain(expiration_date)
        closest_strike_to_latest_price = self.get_closest(latest_price, option_chain.calls["strike"].values)
        straddle_price = self.get_straddle_price(expiration_date=expiration_date, strike=closest_strike_to_latest_price)
        straddle_predicted_movement = self.calculate_straddle_predicted_movement(straddle_price, latest_price)
        straddle_predicted_movement = round(straddle_predicted_movement, 2)
        return straddle_predicted_movement
    
    @staticmethod    
    def today(*args, **kwargs):
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
    def calculate_straddle_predicted_movement(straddle_price, latest_price, *args, **kwargs):
        return 100 * (straddle_price / latest_price)