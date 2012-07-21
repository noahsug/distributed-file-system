from  new_peer_listener import NewPeerListener
from listener_thread import ListenerThread
from sender_thread import SenderThread
from base import Base
import error as err

class Network(Base):
    def __init__(self, dfs):
        Base.__init__(self, dfs)
        self.sender_ = SenderThread(dfs)
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
        lt = ListenerThread(self.dfs_)
        status = lt.connect(dfs)
        if status < 0:
            return status
        self.sender_.addListener(lt)

    def disconnect(self):
        self.log_.v('disconnect')
        self.newPeerListener_.close()

    def getFile(self, fileName, chunksOwned):
        #ask each peer for a random file chunk
        pass

    def fileAdded(self, fileName):
        pass

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
        self.log_('new peer connected')
        pass

