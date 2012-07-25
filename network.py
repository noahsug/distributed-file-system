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
import time

class Network(Base):
    def __init__(self, dfs, fileSystem):
        Base.__init__(self, dfs)
        self.fileSystem_ = fileSystem
        self.knownPeers_ = []
        self.sender_ = None

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
        if not self.dfs_.online:
            self.log_.w('tried to connectTo while offline')
            return

        self.log_.v('connectTo ' + str(dfs.id))
        self.sender_.connectTo(dfs)

    def disconnect(self):
        self.newPeerListener_.close()
        self.sender_.close()

    # ask each peer for a random file chunk until the file is fully retrieved
    def getFile(self, fileName):
        if not self.dfs_.online:
            return err.CannotFullyUpdateFile

        self.log_.v('attempting to get ' + fileName)

        self.fileSystem_.beginLocalUpdate(fileName)
        self.sender_.beginFileFetch(fileName)
        count = 0
        while not self.sender_.isDoneFileFetch():
            time.sleep(.1)
            count += 1
            if count > 100:
                self.log_.w('getting ' + fileName + ' timed out')
                break

        status = self.fileSystem_.finishLocalUpdate(fileName)
        self.log_.v('finished getting ' + fileName + ': ' + str(status))
        return status

    def fileEdited(self):
        if not self.dfs_.online:
            return
        self.sender_.updateAll()

    def getState(self):
        if not self.sender_:
            return self.knownPeers_
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
