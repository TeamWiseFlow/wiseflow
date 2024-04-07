from __future__ import annotations
import logging
import os
from typing import Optional


def _get_logger_level() -> str:
    """
    refer to : https://docs.python.org/3/library/logging.html#logging-levels
    """
    level_map = {
        'silly': 'CRITICAL',
        'verbose': 'DEBUG',
        'info': 'INFO',
        'warn': 'WARNING',
        'error': 'ERROR',
        'silent': 'NOTSET'
    }
    level: str = os.environ.get('WS_LOG', 'info').lower()
    if level not in level_map:
        raise ValueError(
            'WiseFlow LOG should support the values of `silly`, '
            '`verbose`, `info`, `warn`, `error`, `silent`'
        )
    return level_map.get(level, 'info')


def get_logger(name: Optional[str] = None, file: Optional[str] = None) -> logging.Logger:
    """get the logger object
    Args:
        name (str): the logger name
        file (Optional[str], optional): the log file name. Defaults to None.
    Examples:
        logger = get_logger("WechatyPuppet")
        logger = get_logger("WechatyPuppet", file="wechaty-puppet.log")
        logger.info('log info ...')
    Returns:
        logging.Logger: the logger object
    """
    dsw_log = _get_logger_level()

    log_formatter = logging.Formatter(
        fmt='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    # create logger and set level to debug
    logger = logging.getLogger(name)
    logger.handlers = []
    logger.setLevel(dsw_log)
    logger.propagate = False

    # create file handler and set level to debug
    # file = os.environ.get(DSW_LOG_KEY, file)
    if file:
        file_handler = logging.FileHandler(file, 'a', encoding='utf-8')
        file_handler.setLevel(dsw_log)
        file_handler.setFormatter(log_formatter)
        logger.addHandler(file_handler)

    # create console handler and set level to info
    console_handler = logging.StreamHandler()
    console_handler.setLevel(dsw_log)
    console_handler.setFormatter(log_formatter)
    logger.addHandler(console_handler)

    return logger
