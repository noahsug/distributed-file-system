##
# Keeps track of the info of each file.
# - Stores fileName, path, and number of chunks owned.
# - For each file, a count of how many global edits have accumulated on the file.
##

from base import Base
from version import Version

class File(Base):

    def __init__(self, fileName, numChunks, lastEdited):
        self.fileName = fileName
        self.localVersion = Version(fileName, 1, numChunks, lastEdited)
        self.latestVersion = self.localVersion

        self.numChunksOwned = 0
        self.chunksOwned = [False] * numChunks

    def existsLocally(self):
        return self.numChunksTotal == self.numChunksOwned

    def receiveChunk(self, chunkIndex):
        self.chunksOwned[chunkIndex] = True
        self.numChunksOwned += 1
    
    def setVersion(self, version):
        self.localVersion = version
        
    def setNewVersion(self, numEdits, numChunks, lastEdited):
        self.localVersion = Version(self.fileName, numEdits, numChunks, lastEdited)
    
    def getVersion(self):
        return self.localVersion


