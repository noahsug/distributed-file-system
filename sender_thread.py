##
# Sends requests and data to all other peers. Acts as a master of the listener threads.
##

import time

from lock import Lock
from network_thread import NetworkThread
from listener_thread import ListenerThread
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

    def getPeers(self):
        return self.knownPeers_

    def connectToMultiple(self, dfsList):
        for dfs in dfsList:
            self.connectTo(dfs)

    def connectTo(self, dfs):
        self.registerConnDFS(dfs)
        if self.isConnectedTo(dfs):
            self.log_.v('already connected to ' + str(dfs.id))
            return

        lt = ListenerThread(self.dfs_, self.addWork)
        status = lt.connect(dfs)
        if status < 0:
            return status
        self.log_.v('connected to ' + str(dfs.id))
        lt.start()
        self.addListener(lt)

    def addListener(self, listener):
        self.peerLock_.acquire()
        self.listeners_.append(listener)
        self.peerLock_.release()
        self.addUpdateWork(listener)

    def updateAll(self):
        for lt in self.listeners_:
            self.addUpdateWork(lt)

    def addUpdateWork(self, lt):
        state = (self.fileSystem_.getState(), self.getPeers())
        w = work.Work(work.UPDATE, self.dfs_, lt, state)
        self.addWork(w)

    def isConnectedTo(self, dfs):
        if dfs == self.dfs_:
            return True
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

            if self.work_.type == work.UPDATE:
                self.handleUpdate()
            else:
                self.log_.e('received work unkonwn type: ' + self.work_.type)

    def sendWork(self):
        lt = self.work_.dest
        status = lt.sendWork(self.work_)
        if status < 0:
            self.peerLock_.acquire()
            self.listeners_.remove(lt) # other peer has disconnected
            self.peerLock_.release()

    def handleUpdate(self):
        self.log_.v('received update')
        fs, ns = self.work_.data
        self.fileSystem_.updateFiles(fs)
        self.connectToMultiple(ns)

    def close(self):
        self.peerLock_.acquire()
        for listener in self.listeners_:
            listener.close()
        self.peerLock_.release()
        NetworkThread.close(self)
