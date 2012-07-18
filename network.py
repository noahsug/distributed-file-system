class Network:
    def __init__(self, id):
        self.id = id

    ##
    # Public API
    ##
    def connect():
        pass

    def disconnect():
        pass

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

