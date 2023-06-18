from clients import *
from env import *
from scraper import Downloader
import concurrent.futures

from cmds.cmd import Cmd
from log.mixins import LoggingMixin
from log.metaclass import MethodLoggerMeta

__metaclass__ = MethodLoggerMeta


class DownloadAll(Cmd, LoggingMixin):
    def __init__(self, dest_dir, client_username, 
                 client_password, client_mfa,
                 optionslam_username, optionslam_password,
                 ignore, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.dest_dir = dest_dir
        self.client_username = client_username
        self.client_password = client_password
        self.client_mfa = client_mfa
        self.optionslam_username = optionslam_username
        self.optionslam_password = optionslam_password
        self.ignore = ignore

    def execute(self):
        symbols_to_fetch = self.watchlist_symbols()
        with concurrent.futures.ThreadPoolExecutor() as executor:
            future_to_symbol = self.submit_download_to_executor(executor, symbols_to_fetch)
        self.resolve_futures(future_to_symbol)

    def watchlist_symbols(self):
        rh = Robinhood(username=self.client_username, password=self.client_password, mfa_code=self.client_mfa)
        unique = set()
        with rh:
            watchlists_symbols = rh.get_watchlists_symbols()
            watchlists_symbols = self.filter_watchlists(watchlists_symbols)
        for symbols in watchlists_symbols.values():
            if symbols is not None:
                unique.update(symbols)
        return list(unique)

    def filter_watchlists(self, watchlists):
        return {k: v for k, v in watchlists.items() if k not in self.ignore}

    @staticmethod
    def download(ticker, optionslam_username, optionslam_password, file):

        login_payload = {
            "username": optionslam_username,
            "password": optionslam_password,
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
        return f"Finished Downloading symbol: {ticker} to file: {file}"
    
    def get_ticker_destination_file(self, ticker: str):
        return os.path.join(
                    self.get_ticker_data_dir(ticker=ticker),
                    "earnings.csv"
                )

    def get_ticker_data_dir(self, ticker: str):
        return f"{self.data_dir}/{ticker}/"

    def submit_download_to_executor(self, executor, tickers):
        future_to_symbol = dict()
        for ticker in tickers:
            destination_file = self.get_ticker_destination_file(ticker=ticker)
            future = executor.submit(
                self.download,
                ticker,
                self.optionslam_username,
                self.optionslam_password,
                destination_file
            )
            future_to_symbol[future] = ticker
        return future_to_symbol

    def resolve_futures(self, futures):
        for future in concurrent.futures.as_completed(futures):
            res = futures[future]
            try:
                data = future.result()
            except Exception as exc:
                self.log('%r generated an exception: %s' % (res, exc), logging.ERROR)
            else:
                self.log(data)
