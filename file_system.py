##
# Manages the peers local files.
##

from base import Base
from physical_view import PhysicalView
from logical_view import LogicalView
import serializer

class FileSystem(Base):
    def __init__(self, dfs):
        Base.__init__(self, dfs)
        self.physical_ = PhysicalView(dfs)
        self.logical_ = LogicalView(dfs)

    ##
    # Public API
    ##
    def loadFromState(self, state):
        self.logical_ = state
        # TODO: do a check to make sure the physical view matches the logical view

    def add(self, fileName, numChunks):
        self.logical_.add(fileName, numChunks)

    def delete(self, fileName):
        self.logical_.delete(fileName)
        self.physical_.deleteFile(fileName)
    
    def deleteLocalCopy(self, fileName):
        self.physical_.deleteFile(fileName)
    
    def write(self, fileName, buf, offset, bufsize):
        pass

    def isUpToDate(self, fileName):
        return True

    def list(self):
        pass

    def readIntoBuffer(self, fileName, buf, offset, bufsize):
        self.physical_.readIntoBuffer(fileName, buf, offset, bufsize)
        return status

    def gotChunk(self, fileName, chunk):
        pass

    def gotEdit(self, fileName, edit):
        pass

    def serialize(self):
        return serializer.serialize(self.logical_)

    def writeState(self, serializedState):
        self.physical_.writeState(serializedState)

    def readState(self, serializedState):
        pass
    
    def editMade(self, fileName, editor='self'):
        pass

    def hasConflict(self, fileName, numEdits):
        pass


    ##
    # Private methods
    ##
    
    def exists(self, fileName):
        return self.logical_.exists(fileName)

