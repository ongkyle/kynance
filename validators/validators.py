import os

from validators.validator import Validator


class InvalidTickerException(Exception):
    def __init__(self, ticker):
        self.ticker = ticker
        self.message = f"Error: {self.ticker} is an invalid ticker."
        super().__init__(self.message)


class TickerValidator(Validator):
    def __init__(self, ticker, client):
        self.ticker = ticker
        self.client = client

    def validate(self):
        does_exist = self.client.exists(self.ticker)
        if not does_exist:
            raise InvalidTickerException(ticker=self.ticker)


class InvalidOptionException(Exception):

    def __init__(self, ticker):
        self.ticker = ticker
        self.message = f"Error: {self.ticker} does not have an options chain."


class OptionsValidator(Validator):

    def __init__(self, ticker, client):
        self.ticker = ticker
        self.client = client

    def validate(self):
        if not self.supports_options(self.ticker):
            raise InvalidOptionException(self.ticker)

    def supports_options(self, ticker):
        return self.client.get_options_chain(ticker) is not None


class InvalidDataException(Exception):

    def __init__(self, file):
        self.file = file
        self.message = f"Error: {self.file} contains html. A csv file was expected."


class DataValidator(Validator):

    def __init__(self, file):
        self.file = file

    def validate(self):
        if not self.is_valid_data():
            raise InvalidDataException(self.file)

    def is_valid_data(self):
        return not self.does_contain_html()

    def does_contain_html(self):
        out = os.popen(f"grep -rHl '<!' {self.file}").read()
        return out.strip() == self.file
