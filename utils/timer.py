import time
import threading
from utils.logging import get_logger
import traceback

logger = get_logger(__name__)


class setInterval:
    def __init__(self, interval, action):
        self.interval = interval
        self.action = action
        self.stopEvent = threading.Event()
        self.thread = threading.Thread(target=self.__setInterval)
        self.thread.start()

    def __setInterval(self):
        nextTime = time.time()+self.interval
        while not self.stopEvent.wait(nextTime-time.time()):
            nextTime += self.interval
            try:
                self.action()
            except Exception as e:
                logger.error(e)
                traceback.print_exc()

    def cancel(self):
        self.stopEvent.set()
