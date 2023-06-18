from typing import Optional, Tuple
import yaml
import logging
import abc
import os

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
                method_logger = factory.create(
                    method_logger_type=logger_type,
                    logger=logger,
                    obj=value
                )
                attrs_copy[key] = method_logger
        
        name, func = cls.add_logging_member_function()
        attrs_copy[name] = func
        return super(MethodLoggerMeta, cls).__new__(cls, clsname, bases, attrs_copy)

    def add_logging_member_function() -> tuple[str,callable]:
        def log(self, msg: str, level: Optional[int] = logging.INFO):
            logger = logging.getLogger(self.__module__ + "." + "log")
            logger.log(msg=msg, level=level)
        return "log",log
    
    def get_logger_type(cls, key: str, obj: object) -> MethodLoggers:
        is_callable = callable(obj)
        is_public = not key.startswith('__')
        if is_callable and is_public:
            is_static = isinstance(obj, staticmethod)
            if not is_static:
                return MethodLoggers.member
            return MethodLoggers.static
        
    
    def get_logger(obj: object):
        logger = logging.getLogger(obj.__module__ + "." + obj.__qualname__)
        logger.info(f"Initialized logger: {logger.__dict__}")
        return logger
    
    def load_logging_config():
        with open(os.path.expanduser(LOG_CONFIG_FILE) ,"r") as cfg_file:
            logging_cfg = yaml.safe_load(cfg_file)
            logging.config.dictConfig(logging_cfg)