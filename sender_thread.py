##
# Sends requests and data to all other peers. Acts as a master of the listener threads.
##

import time

from lock import Lock
from network_thread import NetworkThread
import dfs_socket

class SenderThread(NetworkThread):
    def __init__(self, dfs):
        NetworkThread.__init__(self, dfs)
        self.listeners_ = []
        self.listenerLock_ = Lock(dfs)
        self.workQueue_ = []
        self.work_ = None

    def addListener(self, listener):
        self.listenerLock_.acquire()
        self.listeners_.append(listener)
        self.listenerLock_.release()

    def close(self):
        self.listenerLock_.acquire()
        for listener in self.listeners_:
            listener.close()
        self.listenerLock_.release()
        NetworkThread.close(self)

    def addWork(self, work):
        self.workQueue_.append(work)

    def doWork(self):
        if len(self.workQueue_) > 0:
            self.work_ = self.workQueue_.pop(0)
            self.processWork()
        else:
            time.sleep(.05)

    def processWork(self):
        self.listenerLock_.acquire()
        for listener in self.listeners_:
            status = listener.sendData(self.work_)
            if status < 0:
                self.listeners_.remove(listener) # other peer has disconnected
        self.listenerLock_.release()


