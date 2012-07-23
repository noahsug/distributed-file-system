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

    def list(self):
        return self.logical_.getFileList()
    
    def readIntoBuffer(self, fileName, buf, offset, bufsize):
        return self.physical_.read(fileName, buf, offset, bufsize)

    def add(self, fileName, numChunks):
        self.logical_.add(fileName, numChunks)

    def delete(self, fileName):
        self.logical_.delete(fileName)
        self.physical_.deleteFile(fileName)

    def deleteLocalCopy(self, fileName):
        self.physical_.deleteFile(fileName)

    def isUpToDate(self, fileName):
        return self.logical_.fileList[fileName].localVersion == self.logical_.fileList[fileName].latestVersion

    def getVersion(self, fileName):
        return self.logical_.getVersion(fileName)
    
    def setVersion(self, fileName, version):
        self.logical_.setVersion(fileName, version)

    def write(self, fileName, buf, offset, bufsize):
        if(self.isUpToDate(fileName)): #if up to date, no conflicts
            self.physical_.write(fileName, buf, offset, bufsize)
            self.logical_.setNewVersion(fileName, self.getVersion(fileName).numEdits + 1, self.physical_.getNumChunks(fileName), self.dfs_.id)
        else: #conflicts
            pass
            
    def writeChunk(self, fileName, chunkNum, data):
        self.physical_.writeChunk(fileName, chunkNum, data)
        self.logical_.fileList[fileName].receiveChunk(chunkNum)

    def loadState(self, serializedState):
        pass

    def writeState(self, serializedState):
        self.physical_.writeState(serializedState)

    def serialize(self):
        return serializer.serialize(self.logical_)

    ##
    # Private methods
    ##

    def exists(self, fileName):
        return self.logical_.exists(fileName)

