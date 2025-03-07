import logging
import os
from datetime import datetime
from threading import Lock


class LoggerSetup:
    _lock = Lock()
    _handlers_set = False

    @classmethod
    def _setup_handlers(cls):
        with cls._lock:
            if not cls._handlers_set:
                # Ensure the log directory exists
                log_dir = "log"
                if not os.path.exists(log_dir):
                    os.makedirs(log_dir)

                # Set up the handlers
                start_time = datetime.now().strftime("%Y-%m-%dT%H_%M_%S")
                file_handler = logging.FileHandler(
                    os.path.join(log_dir, f"{start_time}.log")
                )
                file_handler.setLevel(logging.DEBUG)
                formatter = logging.Formatter(
                    "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
                )
                file_handler.setFormatter(formatter)

                console_handler = logging.StreamHandler()
                console_handler.setLevel(logging.DEBUG)
                console_handler.setFormatter(formatter)

                cls.file_handler = file_handler
                cls.console_handler = console_handler
                cls._handlers_set = True

    @classmethod
    def get_logger(cls, name=None):
        if name is None:
            name = __name__

        logger = logging.getLogger(name)
        logger.setLevel(logging.DEBUG)

        # Ensure handlers are set up only once
        cls._setup_handlers()

        if not logger.hasHandlers():
            logger.addHandler(cls.file_handler)
            logger.addHandler(cls.console_handler)

        return logger


# Usage
def get_logger(name=None):
    return LoggerSetup.get_logger(name)
