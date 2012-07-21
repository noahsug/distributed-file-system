from threading import Thread
from base import Base

class NetworkThread(Base, Thread):
    def __init__(self, dfs):
        Thread.__init__(self)
        Base.__init__(self, dfs)
        self.active_ = True

    def close(self):
        self.active_ = False

    def run(self):
        self.startUp()
        while self.active_:
            self.doWork()
        self.tearDown()

    def startUp(self):
        pass

    def tearDown(self):
        pass
