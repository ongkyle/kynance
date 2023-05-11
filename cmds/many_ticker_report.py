import os
from cmd import Cmd
from robinhood.robinhood import *
from dataframe import *
from scraper import Downloader
from validators.validators import InvalidTickerException, TickerValidator
from strategies.statistics import Statistics
from strategies.mixins import StatisticFactory

class ManyTickerReport(Cmd):
    def __init__(self, days, client_username, client_password, client_mfa, optionslam_username, optionslam_password):
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
        
        data = dict()
        
        for ticker in tickers_with_upcoming_earnings:

            destination_dir = f"/home/kyle/workspace/kynance/data/{ticker}/"
            destination_file = os.path.join(destination_dir, "earnings.csv")

            self.download_if_necessary(ticker, destination_file)

            print (ticker)

            if self.is_valid_data(destination_file) and self.supports_options(ticker) and self.has_mark_price(ticker):
                names = data.get("ticker", [])
                names.append(ticker)    
                data["ticker"] = names  
                data = self.calculate_statistics(data, destination_file, ticker)
        
        df = pd.DataFrame.from_dict(data)
        print (df)
        
            

    
    def get_upcoming_earnings_tickers(self):
        return self.client.get_upcoming_earnings_tickers()


    def download_if_necessary(self, ticker, file):
        if os.path.exists(file):
            return
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
                    download_postfix="/earnings/excel/"+ticker,
                    login_postfix="/accounts/os_login/",
                    csrf_attr="csrfmiddlewaretoken",
                    headers=headers) as d:
            d.download(file)
    
    def calculate_statistics(self, data, source_file, ticker):
        for statistic in Statistics:
            statistic_strategy = self.create_statistic(statistic, source_file, ticker)
            title, stat = statistic_strategy.execute()
            print (statistic.name, stat)
            stats = data.get(title, [])
            if len(stat.index) > 0:
                stats.append(stat[stat.index[0]])
            else:
                stats.append(None)
            data[title] = stats
        return data

    def create_statistic(self, statistic, file, ticker):
        return self.factory.create(statistic, file, ticker)
    
    def is_valid_data(self, file):
        return not self.does_contain_html(file)

    def does_contain_html(self, file):
        out = os.popen(f"grep -rHl '<!' {file}").read()
        return out.strip() == file
    
    def supports_options(self, ticker):
        return self.client.get_options_chain(ticker) != None
    
    def has_mark_price(self, ticker):
        latest_price = self.client.get_latest_price(ticker)
        latest_price = round(latest_price)
        prices = []
        while len(prices) == 0:
            print(latest_price)
            prices = self.client.find_options_mark_price_by_strike(ticker, latest_price)
            print(prices)
            if None in prices:
                return False
            latest_price += 0.5
            latest_price = round(latest_price, 1)
        return True
        