##
# Manages the logically view of the DFS.
##

from base import Base
from file_state import FileState

class View(Base):
    def __init__(self, dfs):
        Base.__init__(self, dfs)
        self.file_state = FileState(dfs)

    def deleteFile(self, fileName):
        pass

    def localCopyDeleted(self, fileName):
        pass

    def addFile(self, fileName, numChunks):
        pass

    def listFiles(self):
        pass
