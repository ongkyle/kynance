from enum import Enum
from typing import Optional

from .robinhood import Robinhood
from .yfinance import YFinance, YFinanceValidation
from .client import Client

class Clients(Enum):
    y_finance = 0
    y_finance_validation = 1
    robinhood = 2
    robinhood_validation = 3

class ClientFactory(object):
    def __init__(self, username: str, password: str, mfa_code: str):
        self.username = username
        self.password = password
        self.mfa_code = mfa_code

    def create(self, client_type: Clients, ticker: str) -> Client:
        print (client_type)
        match client_type:
            case Clients.y_finance.name:
                return YFinance(ticker=ticker)
            case Clients.y_finance:
                return YFinance(ticker=ticker)
            case Clients.y_finance_validation.name:
                return YFinanceValidation()
            case Clients.y_finance_validation:
                return YFinanceValidation()
            case Clients.robinhood.name:
                return Robinhood(username=self.username, 
                                 password=self.password,
                                 mfa_code=self.mfa_code)
            case Clients.robinhood:
                return Robinhood(username=self.username, 
                                 password=self.password,
                                 mfa_code=self.mfa_code)

def create_client(client_type: Clients, 
                  ticker: Optional[str] = None, 
                  username: Optional[str] = None, 
                  password: Optional[str] = None,
                  mfa_code: Optional[str] = None) -> ClientFactory:
    factory = ClientFactory(username=username, password=password, mfa_code=mfa_code)
    return factory.create(client_type=client_type, ticker=ticker)

def create_rh_client(username:str, password:str, mfa_code:str) -> Robinhood:
    return create_client(
        username=username,
        password=password,
        mfa_code=mfa_code,
        client_type=Clients.robinhood
    )

def create_yf_validation_client() -> YFinanceValidation:
    return create_client(
        client_type=Clients.y_finance_validation,
    )