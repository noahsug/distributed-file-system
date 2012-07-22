##
# An API for handling the p2p network operations.
##

from  new_peer_listener import NewPeerListener
from listener_thread import ListenerThread
from sender_thread import SenderThread
from base import Base

import dfs_socket

class Network(Base):
    def __init__(self, dfs):
        Base.__init__(self, dfs)
        self.sender_ = SenderThread(dfs)
        self.sender_.start()
        self.connect()

    ##
    # Public API
    ##
    def connect(self):
        self.log_.v('connect')
        self.newPeerListener_ = NewPeerListener(self.newPeerConnected, self.dfs_)
        self.newPeerListener_.start()

    def join(self, dfs):
        self.log_.v('join')
        lt = ListenerThread(self.dfs_, self.sender_.addWork)
        status = lt.connect(dfs)
        if status < 0:
            self.log_.e('join failed - cannot connect to peer')
            return status
        lt.start()
        self.sender_.addListener(lt)

    def disconnect(self):
        self.log_.v('disconnect')
        self.newPeerListener_.close()
        self.sender_.close()

    def getFile(self, fileName, chunksOwned):
        #ask each peer for a random file chunk
        pass

    def fileAdded(self, fileName):
        self.sender_.addWork('123456789'*5 + dfs_socket.DATA_END)


    def fileDeleted(self, fileName):
        #update each peer that the file has been deleted
        pass

    def fileEdited(self, fileName, edit):
        pass

    def update(self):
        #poll other peers to get up to date file status
        pass

    ##
    # Private methods
    ##
    def newPeerConnected(self, socket):
        self.log_.v('new peer connected')
        lt = ListenerThread(self.dfs_, self.sender_.addWork)
        lt.setConnection(socket)
        lt.start()
        self.sender_.addListener(lt)
