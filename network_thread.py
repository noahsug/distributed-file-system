from threading import Thread
from base import Base

class NetworkThread(Base, Thread):
    def __init__(self, dfs):
        Thread.__init__(self)
        Base.__init__(self, dfs)
        self.active_ = True
        self.running_ = False

    def close(self):
        self.active_ = False

    def run(self):
        self.running_ = True
        self.startUp()
        while self.active_:
            self.doWork()
        self.tearDown()
        self.running_ = False
        self.log_.d('done running')

    def startUp(self):
        pass

    def tearDown(self):
        pass
