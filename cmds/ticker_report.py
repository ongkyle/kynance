import os
from cmd import Cmd
from robinhood.robinhood import *
from dataframe import *
from scraper import Downloader
from validators.validators import InvalidTickerException, TickerValidator
from strategies.statistics import Statistics
from strategies.mixins import StatisticFactory


class TickerReport(Cmd):
    def __init__(self, ticker, days, client_username, client_password, client_mfa, optionslam_username,
                 optionslam_password):
        self.ticker = ticker
        self.days = days
        self.username = client_username
        self.password = client_password
        self.mfa = client_mfa
        self.optionslam_username = optionslam_username
        self.optionslam_password = optionslam_password
        self.factory = StatisticFactory(days, client_username, client_password, client_mfa)
        self.client = Robinhood(username=self.username, password=self.password, mfa_code=self.mfa)
        self.validator = TickerValidator(self.ticker, client=self.client)

    def execute(self):
        self.validate_ticker()

        destination_dir = f"/home/kyle/workspace/kynance/data/{self.ticker}/"
        destination_file = os.path.join(destination_dir, "earnings.csv")

        self.download(destination_file)

        df = Dataframe(destination_file, display_cols=["Earning Date", "Max Move"])

        self.show_statistics(df, destination_file)

    def validate_ticker(self):
        with self.client:
            try:
                self.validator.validate()
            except InvalidTickerException as e:
                raise e

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
            statistic_strategy = self.create_statistic(statistic, source_file)
            title, stat = statistic_strategy.execute()
            titles.append(title)
            df[title] = stat
        df.print(titles)

    def create_statistic(self, statistic, file):
        return self.factory.create(statistic, file)
