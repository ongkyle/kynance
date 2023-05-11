import abc

class Validator(metaclass=abc.ABCMeta):
    def __subclasshook__(cls, subclass):
        return (
            hasattr(subclass, 'validate') and
            callable(subclass.validate)
        ) or NotImplemented
    
    @abc.abstractmethod
    def validate(self):
        raise NotImplemented