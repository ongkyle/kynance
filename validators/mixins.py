from validators.validators import TickerValidator, DataValidator, \
    OptionsValidator, EarningsValidator, Validators
from validators.validator import Validator
from clients.client import ValidationClient


class ValidatorFactory(object):
    def __init__(self, ticker: str, file: str, client: str) -> None:
        self.client = client
        self.ticker = ticker
        self.file = file

    def create(self, validator_type: Validators) -> Validator:
        match validator_type:
            case Validators.ticker:
                return TickerValidator(self.ticker, self.client)
            case Validators.data:
                return DataValidator(file=self.file)
            case Validators.option:
                return OptionsValidator(self.ticker, self.client)
            case Validators.earnings:
                return EarningsValidator(self.ticker, self.client)
        


class ValidatorMixin(object):

    @staticmethod
    def validate(ticker: str, file:str, client: ValidationClient):
        factory = ValidatorFactory(ticker=ticker, file=file, client=client)
        for validator_type in Validators:
            validator = factory.create(validator_type=validator_type)
            validator.validate()

    @staticmethod
    def validate_ticker(ticker: str, client: ValidationClient):
        TickerValidator(ticker, client).validate()

    @staticmethod
    def validate_data(file: str):
        DataValidator(file).validate()

    @staticmethod
    def validate_options(ticker: str, client: ValidationClient):
        OptionsValidator(ticker, client).validate()
    
    @staticmethod
    def validate_earnings(ticker: str, client: ValidationClient):
        EarningsValidator(ticker=ticker, client=client).validate()

