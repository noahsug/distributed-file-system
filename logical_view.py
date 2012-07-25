##
# Represents the logically view of the DFS.
# - Stores which files exist in the DFS.
# - For each file, the # of chunks owned and edit history is stored.
##
import serializer
from base import Base
from lock import Lock
from file import File

class LogicalView(Base):

    def __init__(self, dfs):
        Base.__init__(self, dfs)
        self.lock_ = Lock(dfs)
        self.fileList_ = {}

    def beginLocalUpdate(self, fileName):
        self.fileList_[fileName].chunksOwned = [False] * self.latestVersion.numChunks
        self.fileList_[fileName].numChunksOwned = 0

    def add(self, fileName, fileSize):
        self.lock_.acquire()
        f = File(fileName, 1, fileSize, self.dfs_.id)
        self.fileList_[fileName] = f
        self.lock_.release()

    def delete(self, fileName):
        self.lock_.acquire()
        #del self.fileList_[fileName]
        self.fileList_[fileName].isDeleted = True
        self.lock_.release()

    def exists(self, fileName):
        return (fileName in self.fileList_)

    def getLocalVersion(self, fileName):
        return self.fileList_[fileName].getLocalVersion()

    def getLatestVersion(self, fileName):
        return self.fileList_[fileName].getLatestVersion()

    def setNewVersion(self, fileName, version):
        self.fileList_[fileName].setNewVersion(version)

    def setLocalVersion(self, fileName, numEdits, numChunks, fileSize, lastEdited):
        self.fileList_[fileName].setLocalVersion(numEdits, numChunks, fileSize, lastEdited)

    def getFileList(self):
        return self.fileList_.values()

    def getState(self):
        return self.fileList_

    # update the logical view from the given set of files
    def update(self, files):
        pass
