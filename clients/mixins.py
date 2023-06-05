from enum import Enum

from .robinhood import Robinhood
from .yfinance import YFinance

class Clients(Enum):
    y_finance = 0
    y_finance_validation = 1
    robinhood = 2
    robinhood_validation = 3

class ClientFactory(object):
    def __init__(self, username, password, mfa_code):
        self.username = username
        self.password = password
        self.mfa_code = mfa_code

    def create(self, client_type, ticker):
        print (client_type)
        match client_type:
            case Clients.y_finance.name:
                return YFinance(ticker=ticker)
            case Clients.y_finance:
                return YFinance(ticker=ticker)
            case Clients.robinhood.name:
                return Robinhood(username=self.username, 
                                 password=self.password,
                                 mfa_code=self.mfa_code)
            case Clients.robinhood:
                return Robinhood(username=self.username, 
                                 password=self.password,
                                 mfa_code=self.mfa_code)

def create_client(client_type, ticker=None, username=None, password=None, mfa_code=None):
    factory = ClientFactory(username=username, password=password, mfa_code=mfa_code)
    return factory.create(client_type=client_type, ticker=ticker)   