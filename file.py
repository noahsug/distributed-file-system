##
# Keeps track of the info of each file.
# - Stores fileName, path, and number of chunks owned.
# - For each file, a count of how many global edits have accumulated on the file.
##

from base import Base
from version import Version
import dfs_state

class File(Base):

    def __init__(self, fileName, numEdits, fileSize, lastEdited):
        self.fileName = fileName
        self.localVersion = Version(fileName, numEdits, fileSize, lastEdited)
        self.latestVersion = self.localVersion

        numChunks = int(fileSize / dfs_state.CHUNK_SIZE)
        self.numChunksOwned = 0
        self.chunksOwned = [False] * numChunks
        self.state = ""
        self.readCounter = 0
        self.isDeleted = False

    def existsLocally(self):
        return self.numChunksTotal == self.numChunksOwned

    def receiveChunk(self, chunkIndex):
        if self.chunksOwned[chunkIndex]:
            self.log_.w(self.fileName + ' received chunk ' + chunkIndex + ', but it was already owned!')
            return
        self.chunksOwned[chunkIndex] = True
        self.numChunksOwned += 1

    def setNewVersion(self, version):
        self.localVersion = version
        self.latestVersion = version

    def setLocalVersion(self, numEdits, fileSize, lastEdited):
        self.localVersion = Version(self.fileName, numEdits, fileSize, lastEdited)

    def getLocalVersion(self):
        return self.localVersion

    def getLatestVersion(self):
        return self.latestVersion

    def hasLocalChanges(self):
        return self.localVersion.numEdits > self.latestVersion.numEdits

    def isOutOfDate(self, otherFile=None):
        if otherFile:
            return self.latestVersion.numEdits < otherFile.latestVersion.numEdits
        return self.localVersion.numEdits < self.latestVersion.numEdits

    def __str__(self):
        data = (self.fileName, self.localVersion, self.latestVersion)
        return '%s - local: (%s), latest: (%s)' % data
