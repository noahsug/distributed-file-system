##
# Keeps track of the info of each file.
# - Stores fileName, path, and number of chunks owned.
# - For each file, a count of how many global edits have accumulated on the file.
##

from storage import Storage

class File:
    
    def __init__(self, fileName, filePath, numberChunks):
        self.name = fileName
        self.path = filePath
        self.numChunks = numberChunks
        self.chunks_owned = [False] * numberChunks
        self.numEdits = 0
        self.lastEdited = "peer" + Storage.port
        
    def gotChunk(self, chunk_index):
        self.chunks_owned[chunk_index] = True
    
    def edited(self):
        self.numEdits = self.numEdits + 1
    
    