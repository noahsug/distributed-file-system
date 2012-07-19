import new_peer_listener
from  new_peer_listener import NewPeerListener
import debug
#from debug import Logger

class Network:
    def __init__(self, dfs):
        self.dfs = dfs
#        self.log = Logger('Network')

    ##
    # Public API
    ##
    def connect():
        self.newPeerListener = NewPeerListener(self.newPeerConnected, self.dfs)
        self.newPeerListener.start()

    def disconnect():
        self.newPeerListener.close()

    def getFile(fileName, chunksOwned):
        # ask each peer for a random file chunk
        pass

    def fileAdded(fileName):
        pass

    def fileDeleted(fileName):
        # update each peer that the file has been deleted
        pass

    def fileEdited(fileName, edit):
        pass

    def retired():
        pass

    def update():
        # poll other peers to get up to date file status
        pass

    ##
    # Private methods
    ##
    def newPeerConnected(self, socket):
        pass

