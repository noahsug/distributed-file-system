##
# Represents the logically view of the DFS.
# - Stores which files exist in the DFS.
# - For each file, the # of chunks owned and edit history is stored.
##
import os.path

from base import Base
from lock import Lock
from file import File

class LogicalView(Base):

    def __init__(self, dfs):
        Base.__init__(self, dfs)
        self.lock_ = Lock(dfs)
        self.fileList = {}

    def add(self, fileName, numChunks):
        self.lock_.acquire()
        f = File(fileName, numChunks, self.dfs_.id)
        self.fileList[fileName] = f
        self.lock_.release()
    
    def delete(self, fileName):
        self.lock_.acquire()
        del self.fileList[fileName]
        self.lock_.release()
        
    def exists(self, fileName):
        return (fileName in self.fileList)
    
    def getFileList(self):
        files = []
        for key in self.fileList.keys():
            files.append(os.path.basename(key))
        return files