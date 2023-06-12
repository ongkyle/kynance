from typing import Tuple
import yaml
import logging
import abc

from log.mixins import MethodLoggerFactory, MethodLoggers
from config import LOG_CONFIG_FILE

class MethodLoggerMeta(abc.ABCMeta):
    def __new__(cls, clsname:str, bases:Tuple[type], attrs:dict):
        cls.load_logging_config()
        attrs_copy = attrs.copy()
        factory = MethodLoggerFactory()
        for key, value in attrs.items():
            logger_type = cls.get_logger_type(cls=cls, key=key, obj=value)
            if logger_type is not None:
                logger = cls.get_logger(obj=value)
                print (logger_type)
                method_logger = factory.create(
                    method_logger_type=logger_type,
                    logger=logger,
                    obj=value
                )
                attrs_copy[key] = method_logger
        return super(MethodLoggerMeta, cls).__new__(cls, clsname, bases, attrs_copy)


    def get_logger_type(cls, key: str, obj: object) -> MethodLoggers:
        print (f"{cls} {obj} {key}")
        is_callable = callable(obj)
        is_public = not key.startswith('__')
        if is_callable and is_public:
            is_static = isinstance(obj, staticmethod)
            if not is_static:
                return MethodLoggers.member
            return MethodLoggers.static
        
    
    def get_logger(obj: object):
        logger = logging.getLogger(obj.__module__+ "." + obj.__qualname__)
        logger.info(f"Initialized logger: {logger.__dict__}")
        return logger
    
    def load_logging_config():
        with open(LOG_CONFIG_FILE ,"r") as cfg_file:
            logging_cfg = yaml.safe_load(cfg_file)
            logging.config.dictConfig(logging_cfg)