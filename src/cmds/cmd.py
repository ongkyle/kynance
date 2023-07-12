import abc
from log.metaclass import MethodLoggerMeta


class Cmd(metaclass=MethodLoggerMeta):
    def __subclasshook__(cls, subclass):
        return (
                hasattr(subclass, 'execute') and
                callable(subclass.execute)
        ) or NotImplemented

    @abc.abstractmethod
    def execute(self):
        raise NotImplemented
