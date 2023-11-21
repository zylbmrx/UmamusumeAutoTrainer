import logging
import os
import sys
from logging import Logger
from logging.handlers import QueueHandler
from queue import Queue
import colorlog

from config import CONFIG

log_colors_config = {
    'DEBUG': 'cyan',
    'INFO': 'green',
    'WARNING': 'yellow',
    'ERROR': 'red',
    'CRITICAL': 'bold_red',
}

LogQueue = Queue(maxsize=1000)


def get_log_file_name(clear=False) -> str:
    path = CONFIG.test.log_path
    log_name = CONFIG.test.log_name

    if CONFIG.test.log_path is None:
        path = './log'
    if CONFIG.test.log_name is None:
        log_name = 'log.log'

    if not os.path.exists(CONFIG.test.log_path):
        os.makedirs(CONFIG.test.log_path)
    filename = path + '/' + log_name

    if os.path.isfile(filename) and clear:
        os.remove(filename)

    return filename


def get_log_queue() -> Queue:
    return LogQueue


def get_log_lever(levelStr: str) -> int:
    levelStr = levelStr.upper()

    if levelStr == "DEBUG":
        return logging.DEBUG
    elif levelStr == "INFO":
        return logging.INFO
    elif levelStr == "WARNING" or levelStr == "WARN":
        return logging.WARNING
    elif levelStr == "ERROR":
        return logging.ERROR
    elif levelStr == "CRITICAL" or levelStr == "FATAL":
        return logging.CRITICAL
    else:
        return logging.DEBUG


def get_logger(name) -> Logger:
    logger = logging.getLogger(name)
    logger.propagate = False

    log_level = get_log_lever(CONFIG.test.log_level)
    web_log_level = get_log_lever(CONFIG.test.web_log_level)

    if not logger.handlers:
        logger.setLevel(logging.DEBUG)
        fmt = colorlog.ColoredFormatter(
            fmt='%(log_color)s%(asctime)s  %(levelname)-8s [%(funcName)34s] %(filename)-20s: %(message)s',
            log_colors=log_colors_config
        )
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(fmt)
        console_handler.setLevel(log_level)
        logger.addHandler(console_handler)

        file_handler = logging.FileHandler(get_log_file_name(), encoding='utf-8')
        file_handler.setFormatter(logging.Formatter(
            fmt='%(asctime)s  %(levelname)-8s [%(funcName)20s] %(filename)-20s: %(message)s'))
        file_handler.setLevel(log_level)
        logger.addHandler(file_handler)

        # 输出到队列
        queue_handler = QueueHandler(LogQueue)
        queue_handler.setFormatter(logging.Formatter(
            fmt='%(asctime)s  %(levelname)-8s [%(funcName)20s] %(filename)-20s: %(message)s'))
        queue_handler.setLevel(web_log_level)
        logger.addHandler(queue_handler)

    logger.debug(name + " Logger初始化完成")

    return logger
