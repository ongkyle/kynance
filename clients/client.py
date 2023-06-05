import abc


class ValidationClient(metaclass=abc.ABCMeta):
    def __subclasshook__(cls, subclass):
        return (
                hasattr(subclass, 'exists') and
                callable(subclass.exists) and
                hasattr(subclass, 'supports_options') and
                callable(subclass, 'supports_options')
        ) or NotImplemented

    @abc.abstractmethod
    def exists(self, ticker):
        raise NotImplemented
    
    @abc.abstractmethod
    def supports_options(self, ticker):
        raise NotImplemented
