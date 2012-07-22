##
# Manages the peers local files.
##

from base import Base
from physical_view import PhysicalView
from logical_view import LogicalView

class FileSystem(Base):
    def __init__(self, dfs):
        Base.__init__(self, dfs)
        self.physical_ = PhysicalView(dfs)
        self.logical_ = LogicalView(dfs)

    def delete(self, fileName):
        pass

    def localCopyDeleted(self, fileName):
        pass

    def add(self, fileName, numChunks):
        pass

    def isUpToDate(self, fileName):
        return True

    def list(self):
        pass

    def exists(self, fileName):
        return True

    def readIntoBuffer(self, fileName, buf, offset, bufsize):
        self.physical_.readIntoBuffer(fileName, buf, offset, bufsize)
        return status

    def gotChunk(self, fileName, chunk):
        pass

    def deleteLocalCopy(self, fileName):
        # delete only from storage, not file_state
        pass
