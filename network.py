##
# An API for handling the p2p network operations.
##

from  new_peer_listener import NewPeerListener
from listener_thread import ListenerThread
from sender_thread import SenderThread
from base import Base
import error as err
import work
import dfs_socket

class Network(Base):
    def __init__(self, dfs, fileSystem):
        Base.__init__(self, dfs)
        self.fileSystem_ = fileSystem
        self.knownPeers_ = []

    ##
    # Public API
    ##
    def loadFromState(self, peers):
        self.log_.v('loaded ' + str(len(peers)) + ' peers from disk')
        self.knownPeers_ = peers

    def connect(self):
        self.newPeerListener_ = NewPeerListener(self.newPeerConnected, self.dfs_)
        self.newPeerListener_.start()
        self.sender_ = SenderThread(self.dfs_, self.fileSystem_)
        self.addKnownPeers()
        self.sender_.start()

    def connectTo(self, dfs):
        self.log_.v('join ' + str(dfs.id))
        self.sender_.registerConnDFS(dfs)
        if self.sender_.isConnectedTo(dfs):
            self.log_.v('already connected to ' + str(dfs.id))
            return

        lt = ListenerThread(self.dfs_, self.sender_.addWork)
        status = lt.connect(dfs)
        if status < 0:
            return status
        self.log_.v('connected to ' + str(dfs.id))
        lt.start()
        self.sender_.addListener(lt)
        self.addHandshakeWork(lt)

    def disconnect(self):
        self.newPeerListener_.close()
        self.sender_.close()

    def getFile(self, fileName, chunksOwned):
        # ask each peer for a random file chunk until the file is fully retrieved
        return err.OK

    def fileAdded(self, fileName):
        # TODO for testing purposes
        self.sender_.addWork('123456789'*5 + dfs_socket.DATA_TERMINATOR)

    def fileDeleted(self, fileName):
        #update each peer that the file has been deleted
        pass

    def fileEdited(self, fileName, edit):
        pass

    def update(self):
        #poll other peers to get up to date file status
        pass

    def getState(self):
        return self.sender_.getPeers()

    ##
    # Private methods
    ##
    def newPeerConnected(self, socket):
        self.log_.v('new peer connected')
        lt = ListenerThread(self.dfs_, self.sender_.addWork)
        lt.setConnection(socket)
        lt.start()
        self.sender_.addListener(lt)
        self.addHandshakeWork(lt)

    def addKnownPeers(self):
        for peerDFS in self.knownPeers_:
            self.connectTo(peerDFS)

    def addHandshakeWork(self, lt):
        state = (self.fileSystem_.getState(), self.getState())
        w = work.Work(work.HANDSHAKE, self.dfs_, lt, state)
        self.sender_.addWork(w)
