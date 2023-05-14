from validators.validators import TickerValidator, InvalidTickerException, DataValidator, InvalidDataException, \
    OptionsValidator, InvalidOptionException


class ValidatorMixin(object):

    @staticmethod
    def validate_ticker(ticker, client):
        TickerValidator(ticker, client).validate()

    @staticmethod
    def validate_data(file):
        DataValidator(file).validate()

    @staticmethod
    def validate_options(ticker, client):
        OptionsValidator(ticker, client).validate()
