##
# Keeps track of the state of each file.
# - Stores which files exist in the DFS.
# - For each file, the # of chunks owned and edit history is stored.
##

import os.path

from base import Base
from lock import Lock
from file import File

class FileState(Base):

    def __init__(self, dfs):
        Base.__init__(self, dfs)
        self.lock_ = Lock(dfs)
        self.fileList = {}

    def addFile(self, fileName, numChunks):
        f = File(fileName, numChunks, self.dfs_.id)
        self.fileList['fileName'] = f

    def editMade(self, fileName, editor='self'):
        pass

    def hasConflict(self, fileName, numEdits):
        pass


