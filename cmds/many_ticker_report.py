import concurrent.futures
import os
from collections import deque
from itertools import islice
from typing import List

import numpy as np

from clients import *
from cmds.cmd import Cmd
from dataframe import *
from scraper import Downloader
from strategies.statistics import Statistics
from strategies.mixins import StatisticFactory
from validators.mixins import ValidatorMixin
from clients.mixins import create_client, create_rh_client, Clients


__metaclass__ = MethodLoggerMeta


class ManyTickerReport(Cmd, ValidatorMixin, LoggingMixin):
    def __init__(self, max_workers, tickers, days, client_username, 
                 client_password, client_mfa, optionslam_username,
                 optionslam_password, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.max_workers = max_workers
        self.ticker = tickers
        self.days = days
        self.optionslam_username = optionslam_username
        self.optionslam_password = optionslam_password
        self.rh_client = create_rh_client(username=client_username,
                                          password=client_password, 
                                          mfa_code=client_mfa)
        self.stat_factory = StatisticFactory(days)

    def execute(self):
        tickers_with_upcoming_earnings = self.get_upcoming_earnings_tickers()
        valid_tickers = self.filter_valid_tickers(tickers_with_upcoming_earnings)
        with concurrent.futures.ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            future_to_symbol = self.submit_fn_to_executor(executor,
                                                          self.assemble_data,
                                                          valid_tickers)
        data = self.resolve_futures(future_to_symbol)
        df = pd.DataFrame.from_dict(data)
        df = self.reorder_cols(df)

        print(df.sort_values("profit_probability %", ascending=False))

    @staticmethod
    def reorder_cols(df):
        cols = df.columns.to_list()
        cols = cols[-2:] + cols[:-2]
        df = df[cols]
        return df

    def filter_valid_tickers(self, tickers: List[str]):
        valid_tickers = []
        validation_client = create_client(client_type=Clients.y_finance_validation)
        for ticker in tickers:
            destination_dir = f"{os.getcwd()}/data/{ticker}/"
            destination_file = os.path.join(destination_dir, "earnings.csv")
            self.download_if_necessary(ticker, destination_file)

            try:
                self.validate(
                    ticker=ticker,
                    client=validation_client,
                    file=destination_dir,
                )
            except Exception as e:
                self.log(e, logging.ERROR)
                continue

            valid_tickers.append(ticker)
        
        return valid_tickers

    def calculate_statistics(self, source_file, ticker):
        data = dict()
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
        client = create_client(
            client_type=Clients.y_finance,
            ticker=ticker
        )
        return client.get_next_earnings_date()

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

    def resolve_futures(self, futures):
        data = dict()
        for future in concurrent.futures.as_completed(futures):
            res = futures[future]
            try:
                res = future.result()
            except Exception as exc:
                self.log('%r generated an exception: %s' % (res, exc), logging.ERROR)
            else:
                for k, v in res.items():
                    stats = data.get(k, [])
                    data[k] = np.append(stats, v)
        return data

    @staticmethod
    def skip_this_ticker(seq):
        next(islice(seq, 1, None), None)

    def get_upcoming_earnings_tickers(self):
        tickers = self.rh_client.get_upcoming_earnings_tickers()
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

    def create_statistic(self, statistic: Statistics, file: str, ticker: str):
        client = create_client(client_type=Clients.y_finance, ticker=ticker)
        return self.stat_factory.create(
            stat=statistic,
            file=file,
            ticker=ticker,
            client=client
        )
