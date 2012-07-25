##
# Keeps track of the info of each file.
# - Stores fileName, path, and number of chunks owned.
# - For each file, a count of how many global edits have accumulated on the file.
##

from version import Version
import dfs_state

class File():
    def __init__(self, fileName, numEdits, fileSize, lastEdited):
        self.fileName = fileName
        self.localVersion = Version(fileName, numEdits, fileSize, lastEdited)
        self.latestVersion = self.localVersion.copy()

        numChunks = int(fileSize / dfs_state.CHUNK_SIZE)
        self.numChunksOwned = 0
        self.chunksOwned = [False] * numChunks
        self.state = ""
        self.readCounter = 0
        self.isDeleted = False

    def ownAllChunks(self):
        numChunks = self.localVersion.numChunks
        self.chunksOwned = [True] * numChunks
        self.numChunksOwned = numChunks

    def existsLocally(self):
        return self.localVersion.numChunks == self.numChunksOwned

    def receiveChunk(self, chunkIndex):
        if self.chunksOwned[chunkIndex]:
            self.log_.w(self.fileName + ' received chunk ' + chunkIndex + ', but it was already owned!')
            return
        self.chunksOwned[chunkIndex] = True
        self.numChunksOwned += 1

    def setNewVersion(self, version):
        self.localVersion = version.copy()
        self.latestVersion = version.copy()

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
        data = (self.fileName, self.numChunksOwned, self.localVersion.numChunks, self.localVersion, self.latestVersion)
        return '%s - %d/%d  local: (%s) latest: (%s)' % data
