##
# Represents the version of a file
##

import dfs_state

class Version:
    def __init__(self, fileName, numEdits, fileSize, lastEdited):
        self.fileName = fileName
        self.numEdits = numEdits
        self.numChunks = int(fileSize / dfs_state.CHUNK_SIZE)
        self.lastEdited = lastEdited
        self.fileSize = fileSize

    def equals(self, otherVersion):
        return (self.fileName == otherVersion.fileName and
                self.numEdits == otherVersion.numEdits and
                self.fileSize == otherVersion.fileSize and
                self.lastEdited == otherVersion.lastEdited)

    def __str__(self):
        data = (self.numChunks, self.lastEdited, self.numEdits)
        return 'chunks: %d, edited by: %s, # edits: %d' % data

    def __eq__(self, other):
        return self.equals(other)

    def __ne__(self, other):
        return !self.equals(other)
