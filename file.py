##
# Keeps track of the info of each file.
# - Stores fileName, path, and number of chunks owned.
# - For each file, a count of how many global edits have accumulated on the file.
##

from version import Version

class File():
    def __init__(self, fileName, numEdits, fileSize, lastEdited):
        self.fileName = fileName
        self.localVersion = Version(fileName, numEdits, fileSize, lastEdited)
        self.latestVersion = self.localVersion.copy()

        self.numChunksOwned = 0
        self.chunksOwned = [False] * self.localVersion.numChunks
        self.state = ""
        self.readCounter = 0
        self.isDeleted = False

    def ownAllChunks(self):
        numChunks = self.localVersion.numChunks
        self.chunksOwned = [True] * numChunks
        self.numChunksOwned = numChunks

    def ownNoChunks(self):
        numChunks = self.localVersion.numChunks
        self.chunksOwned = [False] * numChunks
        self.numChunksOwned = 0

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
        self.ownNoChunks()

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
            if self.latestVersion.numEdits < otherFile.latestVersion.numEdits:
                return True
            elif self.latestVersion.numEdits == otherFile.latestVersion.numEdits and self.latestVersion != otherFile.latestVersion:
                # This is a rare race condition. We will loose data here, but it shouldn't happen often.
                return self.latestVersion.lastEdited < otherFile.latestVersion.lastEdited
            else:
                return False
        return self.localVersion.numEdits < self.latestVersion.numEdits

    def __str__(self):
        flags = []
        if self.isOutOfDate():
            flags.append('OutOfDate')
        if self.hasLocalChanges():
            flags.append('LocalChanges')
        if self.existsLocally():
            flags.append('HasLocalCopy')
        flagText = ''
        if len(flags) > 0:
            flagText = ' - ' + ' '.join(flags)

        data = (self.fileName, self.numChunksOwned, self.localVersion.numChunks,
                self.localVersion, self.latestVersion, flagText)
        return '%s - %d/%d  local: (%s) latest: (%s)%s' % data
