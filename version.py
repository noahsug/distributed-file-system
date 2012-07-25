##
# Represents the version of a file
##

import dfs_state

class Version:
    def __init__(self, fileName, numEdits, numChunks, fileSize, lastEdited):
        self.fileName = fileName
        self.numEdits = numEdits
        self.numChunks = int(fileSize / dfs_state.CHUNK_SIZE)
        self.lastEdited = lastEdited
        self.fileSize = fileSize

    def equals(self, otherVersion):
        return (self.fileName == otherVersion.fileName and self.numEdits == otherVersion.numEdits and self.numChunks == otherVersion.numChunks and self.fileSize == otherVersion.fileSize and self.lastEdited == otherVersion.lastEdited)
