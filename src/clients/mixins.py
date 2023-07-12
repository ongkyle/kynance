from enum import Enum
from typing import Optional

from . import ValidationClient, OptionsClient
from .robinhood import Robinhood
from .yfinance import YFinance, YFinanceValidation
from .client import Client
from log.metaclass import MethodLoggerMeta


class Clients(Enum):
    y_finance = 0
    y_finance_validation = 1
    robinhood = 2
    robinhood_validation = 3


class ClientFactory(object, metaclass=MethodLoggerMeta):
    def __init__(self, username: str, password: str, mfa_code: str):
        self.username = username
        self.password = password
        self.mfa_code = mfa_code

    def create(self, client_type: Clients, ticker: str) -> Client:
        if client_type == Clients.y_finance.name:
            return YFinance(ticker=ticker)
        if client_type == Clients.y_finance:
            return YFinance(ticker=ticker)
        if client_type == Clients.y_finance_validation.name:
            return YFinanceValidation()
        if client_type == Clients.y_finance_validation:
            return YFinanceValidation()
        if client_type == Clients.robinhood.name:
            return Robinhood(username=self.username,
                             password=self.password,
                             mfa_code=self.mfa_code)
        if client_type == Clients.robinhood:
            return Robinhood(username=self.username,
                             password=self.password,
                             mfa_code=self.mfa_code)


def create_client(client_type: Clients,
                  ticker: Optional[str] = None,
                  username: Optional[str] = None,
                  password: Optional[str] = None,
                  mfa_code: Optional[str] = None) -> OptionsClient:
    factory = ClientFactory(username=username, password=password, mfa_code=mfa_code)
    return factory.create(client_type=client_type, ticker=ticker)


def create_rh_client(username: str, password: str, mfa_code: str) -> Robinhood:
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
