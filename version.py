##
# Represents the version of a file
##

import dfs_state

class Version:
    def __init__(self, fileName, numEdits, fileSize, lastEdited):
        self.fileName = fileName
        self.numEdits = numEdits
        self.numChunks = int(fileSize / dfs_state.CHUNK_SIZE) + 1
        self.lastEdited = str(lastEdited)
        self.fileSize = fileSize

    def equals(self, otherVersion):
        return (self.fileName == otherVersion.fileName and
                self.numEdits == otherVersion.numEdits and
                self.fileSize == otherVersion.fileSize and
                self.lastEdited == otherVersion.lastEdited)

    def getUpdatedVersion(self, size, peer):
        return Version(self.fileName, self.numEdits + 1, size, peer)

    def copy(self):
        return Version(self.fileName, self.numEdits, self.fileSize, self.lastEdited)

    def __str__(self):
        data = (self.numChunks, self.lastEdited, self.numEdits)
        return '%d | %s %d' % data

    def __eq__(self, other):
        return self.equals(other)

    def __ne__(self, other):
        return not self.equals(other)
