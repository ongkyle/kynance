import os
import sys
from cmd import Cmd
from clients import *
from dataframe import *
from scraper import Downloader
from strategies.statistics import Statistics
from strategies.mixins import StatisticFactory
from clients.mixins import create_client, create_yf_validation_client
from validators.mixins import ValidatorMixin


class TickerReport(Cmd, ValidatorMixin):
    def __init__(self, ticker, days, client_username, client_password, 
                 client_mfa, optionslam_username, optionslam_password,
                 client_type):
        self.ticker = ticker
        self.days = days
        self.optionslam_username = optionslam_username
        self.optionslam_password = optionslam_password
        self.client = create_client(client_type=client_type, username=client_username, 
                                    password=client_password, mfa_code=client_mfa, ticker=ticker)
        self.stat_factory = StatisticFactory(days)

    def execute(self):

        destination_dir = f"{os.getcwd()}/data/{self.ticker}/"
        destination_file = os.path.join(destination_dir, "earnings.csv")

        validation_client = create_yf_validation_client()
        try:
            self.validate(
                ticker=self.ticker,
                client=validation_client,
                file=destination_file
            )
        except Exception as e:
            print(e)
            sys.exit(1)

        self.download(destination_file)

        df = Dataframe(destination_file, display_cols=["Earning Date", "Max Move"])

        self.show_statistics(df, destination_file)

    def download(self, file):

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
                        download_postfix="/earnings/excel/" + self.ticker,
                        login_postfix="/accounts/os_login/",
                        csrf_attr="csrfmiddlewaretoken",
                        headers=headers) as d:
            d.download(file)

    def show_statistics(self, df, source_file):
        titles = []
        for statistic in Statistics:
            print (f"ticker_reporter: {self.ticker} {statistic}")
            statistic_strategy = self.create_statistic(statistic, source_file)
            title, stat = statistic_strategy.execute()
            print (f"ticker_reporter: {self.ticker} {title} {stat}")
            titles.append(title)
            df[title] = stat
        df.print(titles)

    def create_statistic(self, statistic: Statistics, file: str):
        return self.stat_factory.create(stat=statistic,
                                        file=file,
                                        ticker=self.ticker,
                                        client=self.client)
