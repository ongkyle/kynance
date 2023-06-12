import abc
from typing import Optional, Union
from log.metaclass import MethodLoggerMeta

class ValidationClient(metaclass=MethodLoggerMeta):
    def __subclasshook__(cls, subclass):
        return (
                hasattr(subclass, 'exists') and
                callable(subclass.exists) and
                hasattr(subclass, 'supports_options') and
                callable(subclass.supports_options, 'supports_options') and
                hasattr(subclass, 'has_earnings_dates') and
                callable(subclass.has_earnings_dates, 'has_earnings_dates')
        ) or NotImplemented

    @abc.abstractmethod
    def exists(self, ticker) -> bool:
        raise NotImplemented
    
    @abc.abstractmethod
    def supports_options(self, ticker) -> bool:
        raise NotImplemented
    
    @abc.abstractmethod
    def has_future_earnings_dates(self, ticker) -> bool:
        raise NotImplemented

class OptionsClient(metaclass=MethodLoggerMeta):
    def __subclasshook__(cls, subclass):
        return (
            hasattr(subclass, 'get_straddle_predicted_movement') and
            callable(subclass.get_straddle_predicted_movement)
        )
    
    @abc.abstractmethod
    def get_straddle_predicted_movement(self, symbol: Optional[str]) -> float:
        raise NotImplemented

Client = Union[ValidationClient, OptionsClient]