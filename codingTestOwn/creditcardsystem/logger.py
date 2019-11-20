# -*- coding: utf-8 -*-
import logging

LOGGER_DISABLED = False
logger_dict = {}

def loggers(name):
    global logger_dict

    if logger_dict.get(name):
        return logger_dict.get(name)
    else:
        mylogger = logging.getLogger('Hansangyoon')
        handler = logging.FileHandler('../processing.log')
        handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)7s - %(message)s', '%Y-%m-%d %H:%M'))
        handler.setLevel(logging.INFO)
        mylogger.addHandler(handler)
        mylogger.setLevel(logging.INFO)
        mylogger.disabled = LOGGER_DISABLED
        logger_dict.update(dict(logger=mylogger))
    return mylogger
