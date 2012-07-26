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
import error as err

class SenderThread(NetworkThread):
    def __init__(self, dfs, fileSystem):
        NetworkThread.__init__(self, dfs)
        self.fileSystem_ = fileSystem
        self.listeners_ = []
        self.peerLock_ = Lock(dfs, 'peer')
        self.workQueue_ = []
        self.work_ = None
        self.knownPeers_ = set()
        self.fileFetchStatus = []

    def isDoneFileFetch(self):
        return len(self.fileFetchStatus) == 0

    def getPeers(self):
        return self.knownPeers_

    def connectToMultiple(self, dfsList):
        for dfs in dfsList:
            self.connectTo(dfs)

    def connectTo(self, dfs):
        if self.isConnectedTo(dfs):
            self.log_.v('already connected to ' + str(dfs.id))
            return
        self.registerConnDFS(dfs)

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
        self.peerLock_.acquire()
        for lt in self.listeners_:
            self.addUpdateWork(lt)
        self.peerLock_.release()

    def beginFileFetch(self, fileName):
        ltList = []
        self.peerLock_.acquire()
        self.fileFetchStatus = []
        for lt in self.listeners_:
            self.fileFetchStatus.append(lt)
            ltList.append(lt)
        self.peerLock_.release()

        for lt in ltList:
            self.addChunkRequestWork(lt, fileName)

    def editPropagated(self):
        # due to time constraints, I'm using this rather simple implementation
        time.sleep(1)
        return True

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
        self.log_.v('registering new peer: ' + dfs.id.str)
        self.knownPeers_.add(dfs)

    def addWork(self, work):
        self.workQueue_.append(work)

    def doWork(self):
        if len(self.workQueue_) > 0:
            self.work_ = self.workQueue_.pop(0)
            self.processWork()
        else:
            self.removeDisconnectedListeners()
            time.sleep(.03)

    def removeDisconnectedListeners(self):
        self.peerLock_.acquire()
        for lt in self.listeners_:
            if not lt.active_:
                self.log_.v('detected that ' + lt.getConnDFS().id.str + ' has disconnected')
                self.removeListener(lt)
        self.peerLock_.release()

    def processWork(self):
        if self.work_.source.id == self.dfs_.id:
            self.sendWork()
        else:
            lt = self.work_.dest
            if lt.getConnDFS().isInit():
                self.knownPeers_.add(lt.getConnDFS())

            if self.work_.type == work.UPDATE:
                self.handleUpdate()
            elif self.work_.type == work.CHUNK_REQUEST:
                self.handleChunkRequest()
            elif self.work_.type == work.CHUNK_RESPONSE:
                self.handleChunkResponse()
            elif self.work_.type == work.NO_CHUNK:
                self.handleNoChunk()
            else:
                self.log_.e('received work unkonwn type: ' + self.work_.type)

    def sendWork(self):
        lt = self.work_.dest
        status = lt.sendWork(self.work_)
        if status < 0:
            self.peerLock_.acquire()
            self.log_.v('trying to send work, but ' + lt.getConnDFS().id.str + ' has disconnected')
            self.removeListener(lt)
            self.peerLock_.release()

    def removeListener(self, lt):
        if lt in self.fileFetchStatus:
            self.fileFetchStatus.remove(lt)
        self.listeners_.remove(lt) # other peer has disconnected

    def handleUpdate(self):
        lt = self.work_.dest
        self.log_.v('received update from ' + str(lt.getConnDFS().id))
        fs, ns = self.work_.data
        status = self.fileSystem_.updateFiles(fs)
        self.connectToMultiple(ns)
        if status == err.CausedConflict:
            self.log_.v('update from ' + str(lt.getConnDFS().id) + ' caused conflict, updating all peers')
            self.updateAll()

    def handleNoChunk(self):
        lt = self.work_.dest
        self.peerLock_.acquire()
        if lt in self.fileFetchStatus:
            self.log_.v(lt.getConnDFS().id.str + ' is no longer providing chunks')
            self.fileFetchStatus.remove(lt)
        self.peerLock_.release()

    def handleChunkRequest(self):
        fileName, missingChunks = self.work_.data
        lt = self.work_.dest
        chunkInfo = self.fileSystem_.getRandomChunk(fileName, missingChunks)
        self.addChunkResponseWork(chunkInfo, fileName)

    def handleChunkResponse(self):
        lt = self.work_.dest
        fileName, chunkNum, chunkData = self.work_.data
        self.log_.v(lt.getConnDFS().id.str + ' received chunk ' + str(chunkNum) + ' of ' + fileName)
        self.fileSystem_.writeChunk(fileName, chunkNum, chunkData)
        self.addChunkRequestWork(lt, fileName)

    def addUpdateWork(self, lt):
        state = (self.fileSystem_.getState(), self.getPeers())
        w = work.Work(work.UPDATE, self.dfs_, lt, state)
        self.log_.v('sending an update to ' + lt.getConnDFS().id.str)
        self.addWork(w)

    def addChunkRequestWork(self, lt, fileName):
        missingChunks = self.fileSystem_.getMissingChunks(fileName)
        if missingChunks == None:
            self.log_.v(fileName + ' is no longer missing chunks. File retrieval complete')
            self.handleNoChunk()
            return
        data = (fileName, missingChunks)
        w = work.Work(work.CHUNK_REQUEST, self.dfs_, lt, data)
        self.log_.v('requesting a chunk of ' + fileName + ' from ' + lt.getConnDFS().id.str)
        self.addWork(w)

    def addChunkResponseWork(self, chunkInfo, fileName):
        lt = self.work_.dest
        type = ''
        if chunkInfo:
            type = work.CHUNK_RESPONSE
            fileName, chunkNum, chunkData = chunkInfo
            self.log_.v('sending chunk ' + str(chunkNum) + ' of ' + fileName + ' to ' + lt.getConnDFS().id.str)
        else:
            self.log_.v('do not have ' + fileName + ' chunk for ' + lt.getConnDFS().id.str)
            type = work.NO_CHUNK

        w = work.Work(type, self.dfs_, lt, chunkInfo)
        self.addWork(w)

    def close(self):
        self.log_.d('close started')
        self.peerLock_.acquire()
        for listener in self.listeners_:
            listener.close()
        self.peerLock_.release()
        self.waitForListenersToClose()
        NetworkThread.close(self)
        self.log_.d('close finished')

    def waitForListenersToClose(self):
        self.log_.d('waitForListenersToClose started')
        self.peerLock_.acquire()
        lts = list(self.listeners_)
        self.peerLock_.release()
        for lt in lts:
            lt.join()
        self.log_.d('waitForListenersToClose finished')
