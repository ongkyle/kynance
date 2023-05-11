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