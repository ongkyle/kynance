import concurrent.futures
import os
from collections import deque
from itertools import islice

import numpy as np

from cmd import Cmd
from robinhood.robinhood import *
from dataframe import *
from scraper import Downloader
from strategies.statistics import Statistics
from strategies.mixins import StatisticFactory
from validators.mixins import ValidatorMixin


class ManyTickerReport(Cmd, ValidatorMixin):
    def __init__(self, max_workers, tickers, days, client_username, client_password, client_mfa, optionslam_username,
                 optionslam_password):
        self.max_workers = max_workers
        self.ticker = tickers
        self.days = days
        self.username = client_username
        self.password = client_password
        self.mfa = client_mfa
        self.optionslam_username = optionslam_username
        self.optionslam_password = optionslam_password
        self.factory = StatisticFactory(days, client_username, client_password, client_mfa)
        self.client = Robinhood(username=self.username, password=self.password, mfa_code=self.mfa)

    def execute(self):
        tickers_with_upcoming_earnings = self.get_upcoming_earnings_tickers()
        valid_tickers = self.filter_valid_tickers(tickers_with_upcoming_earnings)
        print (self.max_workers)
        with concurrent.futures.ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            future_to_symbol = self.submit_fn_to_executor(executor,
                                                          self.assemble_data,
                                                          valid_tickers)
        data = self.resolve_futures(future_to_symbol)
        df = pd.DataFrame.from_dict(data)

        df = self.reorder_cols(df)
        print(df)

    @staticmethod
    def reorder_cols(df):
        cols = df.columns.to_list()
        cols = cols[-2:] + cols[:-2]
        df = df[cols]
        return df

    def filter_valid_tickers(self, tickers):
        valid_tickers = []
        print (self.max_workers)
        for idx, ticker in enumerate(tickers):
            destination_dir = f"{os.getcwd()}/data/{ticker}/"
            destination_file = os.path.join(destination_dir, "earnings.csv")
            self.download_if_necessary(ticker, destination_file)

            try:
                self.validate_ticker(ticker, self.client)
                self.validate_data(destination_file)
                self.validate_options(ticker, self.client)
            except Exception as e:
                print(e)
                continue

            valid_tickers.append(ticker)

        return valid_tickers

    def calculate_statistics(self, source_file, ticker):
        data = dict()
        print (f"Calculating Statistics: {ticker}")
        for statistic in Statistics:
            statistic_strategy = self.create_statistic(statistic, source_file, ticker)
            title, stat = statistic_strategy.execute()
            stats = data.get(title, [])
            if len(stat.index) > 0:
                stats.append(stat[stat.index[0]])
            else:
                stats.append(None)
            data[title] = stats
        return data

    def assemble_data(self, ticker, destination_file):
        data = self.calculate_statistics(destination_file, ticker)

        names = data.get("ticker", [])
        names.append(ticker)
        data["ticker"] = names

        data["earning date"] = self.get_next_earning_date(ticker)
        return data

    def get_next_earning_date(self, ticker):
        return self.client.get_next_earnings_date(ticker)

    @staticmethod
    def submit_fn_to_executor(executor, fn, tickers):
        future_to_symbol = dict()
        for symbol in tickers:
            destination_dir = f"/{os.getcwd()}/data/{symbol}/"
            destination_file = os.path.join(destination_dir, "earnings.csv")
            future = executor.submit(
                fn,
                symbol,
                destination_file
            )
            future_to_symbol[future] = symbol
        return future_to_symbol

    @staticmethod
    def resolve_futures(futures):
        data = dict()
        for future in concurrent.futures.as_completed(futures):
            res = futures[future]
            try:
                res = future.result()
            except Exception as exc:
                print('%r generated an exception: %s' % (res, exc))
            else:
                for k, v in res.items():
                    stats = data.get(k, [])
                    data[k] = np.append(stats, v)
        return data

    @staticmethod
    def skip_this_ticker(seq):
        next(islice(seq, 1, None), None)

    def get_upcoming_earnings_tickers(self):
        tickers = self.client.get_upcoming_earnings_tickers()
        return deque(tickers)

    def download_if_necessary(self, ticker, file):
        if not os.path.exists(file):
            self.download(ticker, file)

    def download(self, ticker, file):

        login_payload = {
            "username": self.optionslam_username,
            "password": self.optionslam_password,
            "next": "/"
        }

        headers = {
            "Upgrade-Insecure-Requests": "1",
            "Sec-Fetch-Dest": "document",
            "Sec-Fetch-Mode": "navigate",
            "Sec-Fetch-Site": "same-origin",
            "Connection": "keep-alive",
            "Origin": "https://www.optionslam.com",
            "Host": "www.optionslam.com",
            "Method": "POST",
            "Referer": "https://www.optionslam.com/accounts/login/",
            "Content-Type": "application/x-www-form-urlencoded",
            "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:109.0) Gecko/20100101 Firefox/112.0"
        }

        with Downloader(needs_login=True, login_payload=login_payload,
                        base_url="https://www.optionslam.com",
                        download_postfix="/earnings/excel/" + ticker,
                        login_postfix="/accounts/os_login/",
                        csrf_attr="csrfmiddlewaretoken",
                        headers=headers) as d:
            d.download(file)

    def create_statistic(self, statistic, file, ticker):
        return self.factory.create(statistic, file, ticker)
