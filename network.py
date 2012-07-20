from  new_peer_listener import NewPeerListener
from debug import Logger

class Network:
    def __init__(self, dfs):
        self.dfs_ = dfs
        self.log_ = Logger('Network', self.dfs_)
        self.log_.d('init')

    ##
    # Public API
    ##
    def connect():
        self.log_('connect')
        self.newPeerListener = NewPeerListener(self.newPeerConnected, self.dfs_)
        self.newPeerListener.start()

    def disconnect():
        self.log_('disconnect')
        self.newPeerListener.close()

    def getFile(fileName, chunksOwned):
        #ask each peer for a random file chunk
        pass

    def fileAdded(fileName):
        pass

    def fileDeleted(fileName):
        #update each peer that the file has been deleted
        pass

    def fileEdited(fileName, edit):
        pass

    def retired():
        pass

    def update():
        #poll other peers to get up to date file status
        pass

    ##
    # Private methods
    ##
    def newPeerConnected(self, socket):
        self.log('new peer connected')
        pass

