##
# Sends requests and data to all other peers. Acts as a master of the listener threads.
##

import time

from lock import Lock
from network_thread import NetworkThread
import serializer
import dfs_socket
import dfs_state
import work

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
        self.log_.v('processing work of type ' + self.work_.type)
        if self.work_.type == work.HANDSHAKE:
            if self.work_.source.id == self.dfs.id:
                self.handleGiveHandshake()

    def handleGiveHandshake(self):
        lt = self.work_.data
        self.work_.type = work.ACCEPT_HANDSHAKE
        self.work_.data = self.dfs_
        self.sendWork(lt)

    def sendWork(self, lt):
        data = serializor.serialize(self.work_)
        status = lt.sendData(data)
        if status < 0:
            self.listenerLock_.acquire()
            self.listeners_.remove(lt) # other peer has disconnected
            self.listenerLock_.release()

    def getPeers(self):
        peers = []
        for listener in self.listeners_:
            if listener.hasConnDFS():
                peers.append(listener.getConnDFS())
        return peers
