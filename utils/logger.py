from os import getenv, path
from dotenv import load_dotenv
from enum import Enum
import inspect
from datetime import datetime


class LogLevels(Enum):
    FULL = 50
    DEBUG = 40
    INFO = 30
    WARNING = 20
    ERROR = 10
    SILENT = 0

load_dotenv()
LOG_LEVEL = getenv('LOG_LEVEL', 'SILENT')


def __get_caller__():
    # will always have access to two stack frames down, since this is called from
    # our static methods here
    return path.basename(inspect.stack()[2].filename)


class Logger:

    def update_level(level):
        global LOG_LEVEL
        LOG_LEVEL = level

    def FULL(msg):
        if LogLevels[LOG_LEVEL].value >= LogLevels.FULL.value:
            t = datetime.now().isoformat()
            print(f"{t} [{__get_caller__()}] FULL: {msg}")

    def DEBUG(msg):
        if LogLevels[LOG_LEVEL].value >= LogLevels.DEBUG.value:
            t = datetime.now().isoformat()
            print(f"{t} [{__get_caller__()}] DEBUG: {msg}")

    def INFO(msg):
        if LogLevels[LOG_LEVEL].value >= LogLevels.INFO.value:
            t = datetime.now().isoformat()
            print(f"{t} [{__get_caller__()}] INFO: {msg}")

    def WARNING(msg):
        if LogLevels[LOG_LEVEL].value >= LogLevels.WARNING.value:
            t = datetime.now().isoformat()
            print(f"{t} [{__get_caller__()}] WARNING: {msg}")

    def ERROR(msg):
        if LogLevels[LOG_LEVEL].value >= LogLevels.ERROR.value:
            t = datetime.now().isoformat()
            print(f"{t} [{__get_caller__()}] ERROR: {msg}")
