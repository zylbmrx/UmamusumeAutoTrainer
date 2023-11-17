import logging
import os
import sys
from logging import Logger
from logging.handlers import QueueHandler
from queue import Queue
import colorlog

log_colors_config = {
    'DEBUG': 'cyan',
    'INFO': 'green',
    'WARNING': 'yellow',
    'ERROR': 'red',
    'CRITICAL': 'bold_red',
}
FileName = 'log.log'
LogQueue = Queue(maxsize=1000)


def set_file_name(filename, clear=False):
    global FileName
    FileName = filename
    if os.path.isfile(FileName) and clear:
        os.remove(FileName)


def get_log_queue() -> Queue:
    return LogQueue


def get_logger(name) -> Logger:
    logger = logging.getLogger(name)
    logger.propagate = False
    if not logger.handlers:
        logger.setLevel(logging.DEBUG)
        fmt = colorlog.ColoredFormatter(
            fmt='%(log_color)s%(asctime)s  %(levelname)-8s [%(funcName)34s] %(filename)-20s: %(message)s',
            log_colors=log_colors_config
        )
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(fmt)
        console_handler.setLevel(logging.DEBUG)
        logger.addHandler(console_handler)

        file_handler = logging.FileHandler(FileName, encoding='utf-8')
        file_handler.setFormatter(logging.Formatter(
            fmt='%(asctime)s  %(levelname)-8s [%(funcName)20s] %(filename)-20s: %(message)s'))
        file_handler.setLevel(logging.DEBUG)
        logger.addHandler(file_handler)

        # 输出到队列
        queue_handler = QueueHandler(LogQueue)
        queue_handler.setFormatter(logging.Formatter(
            fmt='%(asctime)s  %(levelname)-8s [%(funcName)20s] %(filename)-20s: %(message)s'))
        logger.addHandler(queue_handler)


    logger.debug(name + " Logger初始化完成")

    return logger
