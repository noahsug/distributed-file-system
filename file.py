##
# Keeps track of the info of each file.
# - Stores fileName, path, and number of chunks owned.
# - For each file, a count of how many global edits have accumulated on the file.
##

class File():

    def __init__(self, fileName, numChunks, lastEdited):
        self.name = fileName
        self.numChunksTotal = numChunks
        self.numChunksOwned = 0
        self.chunksOwned = [False] * numberChunks
        self.numEdits = 1
        self.lastEdited = lastEdited

    def existsLocally(self):
        return self.numChunksTotal == self.numChunksOwned

    def gotChunk(self, chunkIndex):
        self.chunksOwned[chunkIndex] = True
        self.numChunksOwned += 1

    def edited(self):
        self.numEdits = self.numEdits + 1


