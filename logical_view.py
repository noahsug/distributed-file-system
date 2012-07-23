##
# Represents the logically view of the DFS.
# - Stores which files exist in the DFS.
# - For each file, the # of chunks owned and edit history is stored.
##
import os.path

import serializer
from base import Base
from lock import Lock
from file import File

class LogicalView(Base):

    def __init__(self, dfs):
        Base.__init__(self, dfs)
        self.lock_ = Lock(dfs)
        self.fileList_ = {}

    def add(self, fileName, numChunks):
        self.lock_.acquire()
        f = File(fileName, numChunks, self.dfs_.id)
        self.fileList_[fileName] = f
        self.lock_.release()

    def delete(self, fileName):
        self.lock_.acquire()
        del self.fileList_[fileName]
        self.lock_.release()

    def exists(self, fileName):
        return (fileName in self.fileList_)

    def getVersion(self, fileName):
        return self.fileList_[fileName].getVersion()

    def setVersion(self, fileName, version):
        self.fileList_[fileName].setVersion(version)

    def setNewVersion(self, fileName, numEdits, numChunks, lastEdited):
        self.fileList_[fileName].setNewVersion(numEdits, numChunks, lastEdited)

    def getFileList(self):
        files = []
        for key in self.fileList_.keys():
            files.append(os.path.basename(key))
        return files

    def serialize(self):
        return serializer.serialize(self.fileList_)

    # update the logical view from the given set of files
    def update(self, files):
        pass
