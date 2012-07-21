from  new_peer_listener import NewPeerListener
from base import Base

class Network(Base):
    def __init__(self, dfs):
        Base.__init__(self, dfs)
        self.connect()

    ##
    # Public API
    ##
    def connect(self):
        self.log_.d('connect')
        self.newPeerListener = NewPeerListener(self.newPeerConnected, self.dfs_)
        self.newPeerListener.start()

    def join(self, dfs):
        pass

    def disconnect(self):
        self.log_.d('disconnect')
        self.newPeerListener.close()

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

