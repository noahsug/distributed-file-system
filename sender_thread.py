##
# Sends requests and data to all other peers. Acts as a master of the listener threads.
##

import time

from lock import Lock
from network_thread import NetworkThread
import dfs_socket
import dfs_state
import work

class SenderThread(NetworkThread):
    def __init__(self, dfs, fileSystem):
        NetworkThread.__init__(self, dfs)
        self.fileSystem_ = fileSystem
        self.listeners_ = []
        self.peerLock_ = Lock(dfs)
        self.workQueue_ = []
        self.work_ = None
        self.knownPeers_ = set()

    def isConnectedTo(self, dfs):
        val = False
        self.peerLock_.acquire()
        for lt in self.listeners_:
            if lt.getConnDFS() == dfs:
                val = True
                break
        self.peerLock_.release()
        return val

    def registerConnDFS(self, dfs):
        self.knownPeers_.add(dfs)

    def addListener(self, listener):
        self.peerLock_.acquire()
        self.listeners_.append(listener)
        self.peerLock_.release()

    def close(self):
        self.peerLock_.acquire()
        for listener in self.listeners_:
            listener.close()
        self.peerLock_.release()
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
        if self.work_.source.id == self.dfs_.id:
            self.sendWork()
        else:
            lt = self.work_.dest
            if lt.getConnDFS().isInit():
                self.knownPeers_.add(lt.getConnDFS())

            if self.work_.type == work.HANDSHAKE:
                self.handleHandshake()
            else:
                self.log_.e('received work unkonwn type: ' + self.work_.type)

    def sendWork(self):
        lt = self.work_.dest
        status = lt.sendWork(self.work_)
        if status < 0:
            self.peerLock_.acquire()
            self.listeners_.remove(lt) # other peer has disconnected
            self.peerLock_.release()

    def handleHandshake(self):
        self.log_.v('received handshake')
        fs, ns = self.work_.data

    def getPeers(self):
        return self.knownPeers_
