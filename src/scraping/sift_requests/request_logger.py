import logging
import os

from datetime import datetime

log_dir = os.environ["SCRAPE_LOGS"]
class Logger:
    loggers = []
    @staticmethod
    def get(name: str, mode: str = "a"):
        name = name
        log_file_name = name + (f"-{datetime.now().strftime("%d-%m-%Y")}")
        logfile = os.path.join(log_dir, log_file_name)
        logger = logging.Logger(name=name)
        f_handler = logging.FileHandler(logfile, mode=mode)
        logger.addHandler(f_handler)
        Logger.loggers.append(logger)
        return logger

    @staticmethod
    def get_existing(name):  # noqa: N805
        return logging.getLogger(name=name)
