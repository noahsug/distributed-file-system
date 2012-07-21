##
# Sends requests and data to all other peers. Acts as a master of the listener threads.
##

from lock import Lock
from network_thread import NetworkThread
import dfs_socket

class SenderThread(NetworkThread):
    def __init__(self, dfs):
        NetworkThread.__init__(self, dfs)
        self.listeners_ = []
        self.listenerLock_ = Lock(dfs)

    def addListener(self, listener):
        self.listenerLock_.acquire()
        self.listeners_.append(listener)
        self.listenerLock_.release()

    def close():
        self.listenerLock_.acquire()
        for listener in self.listeners_:
            listener.close()
        self.listenerLock_.release()
        NetworkThread.close()

    def run():
        pass


