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
        self.sender_.connectToMultiple(self.knownPeers_)
        self.sender_.start()

    def connectTo(self, dfs):
        self.log_.v('connectTo ' + str(dfs.id))
        self.sender_.connectTo(dfs)

    def disconnect(self):
        self.newPeerListener_.close()
        self.sender_.close()

    # ask each peer for a random file chunk until the file is fully retrieved
    def getFile(self, fileName):
        self.fileSystem_.beginLocalUpdate(fileName)
        self.sender_.beginFileFetch(fileName)
        while not self.sender_.isDoneFileFetch():
            time.sleep(.1)
        status = self.fileSystem_.finishLocalUpdate(fileName)
        self.log_.v('finished getting ' + fileName + ': ' + status)
        return status

    def fileEdited(self):
        self.sender_.updateAll()

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
