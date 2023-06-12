import logging
from enum import Enum
from typing import Optional

class MethodLoggers(Enum):
    member = 0
    static = 1

class Loggers:
    def member_method_logger(method:callable, logger:logging.Logger):
        def inner(self, *args, **kwargs):
            logger.info(f"starting | args: {args} | kwargs: {kwargs}")
            # print(logger.__dict__, name, args, kwargs)
            res = method(self, *args, **kwargs)
            logger.info(f"finished | args: {args} | kwargs: {kwargs} | returns: {res}")
            return res
    
        return inner
    
    def static_method_logger(method:callable, logger:logging.Logger):
        def inner(self, *args, **kwargs):
            logger.info(f"Starting | args: {args} | kwargs: {kwargs}")
            res = method(*args, **kwargs)
            logger.info(f"Finished | args: {args} | kwargs: {kwargs} | returns: {res}")
            return res
        
        return inner

class MethodLoggerFactory(object):
    
    def create(self, method_logger_type: MethodLoggers, logger: logging.Logger, obj: object):
        match method_logger_type:
            case MethodLoggers.member:
                method_logger = Loggers.member_method_logger(
                    method=obj,
                    logger=logger)
                logger.info(f"Creating MethodLogger: {method_logger}")
                return method_logger
            case MethodLoggers.static:
                method_logger = Loggers.static_method_logger(
                    method=obj,
                    logger=logger)
                logger.info(f"Creating MethodLogger: {method_logger}")
                return method_logger
            

class LoggingMixin:
    pass
    


