##
# Manages the peers local files.
##

from base import Base
from version import Version
from physical_view import PhysicalView
from logical_view import LogicalView
import error as err

class FileSystem(Base):
    def __init__(self, dfs):
        Base.__init__(self, dfs)
        self.physical_ = PhysicalView(dfs)
        self.logical_ = LogicalView(dfs)

    ##
    # Public API
    ##
    def loadFromState(self, state):
        self.logical_.update(state)
        # TODO: do a check to make sure the physical view matches the logical view

    def list(self):
        return self.logical_.getFileList()

    def readIntoBuffer(self, fileName, buf, offset, bufsize):
        return self.physical_.read(fileName, buf, offset, bufsize)

    def add(self, fileName, numChunks):
        self.logical_.add(fileName, self.physical_.getFileSize(fileName), numChunks)

    def delete(self, fileName):
        self.logical_.delete(fileName)
        self.physical_.deleteFile(fileName)

    def deleteLocalCopy(self, fileName):
        self.physical_.deleteFile(fileName)

    def isUpToDate(self, fileName):
        return self.logical_.fileList[fileName].localVersion.equals(self.logical_.fileList[fileName].latestVersion)

    def isNeedUpdate(self, fileName):
        return self.logical_.fileList[fileName].localVersion.before(self.logical_.fileList[fileName].latestVersion)

    def getVersion(self, fileName):
        return self.logical_.getVersion(fileName)

    def write(self, fileName, buf, offset, bufsize):

        if self.isUpToDate(fileName): #if up to date, no conflicts
            self.physical_.write(fileName, buf, offset, bufsize)
            ver = Version(fileName, self.getVersion(fileName).numEdits + 1, self.physical_.getNumChunks(fileName), self.physical_.getFileSize(fileName), self.dfs_.id)
            self.logical_.setNewVersion(fileName, ver)
            return err.OK
        elif self.isNeedUpdate(fileName): #local < latest, conflict (update failed)
            conflictName = fileName + '.' + self.dfs_.id
            self.physical_.copyFile(fileName, conflictName)
            self.physical_.write(conflictName, buf, offset, bufsize)
            self.add(conflictName, self.physical_.getNumChunks(conflictName))
            return conflictName
        else: #latest > local, offline edits
            self.physical_.write(fileName, buf, offset, bufsize)
            self.logical_.setLocalVersion(fileName, self.getVersion(fileName).numEdits + 1, self.physical_.getNumChunks(fileName), self.physical_.getFileSize(fileName), self.dfs_.id)
            return err.OK

    def writeChunk(self, fileName, chunkNum, data):
        
        if not self.physical_.exists(fileName):
            self.physical_.fillEmptyFile(fileName, self.logical_.fileList_[fileName].latestVersion.fileSize)
        
        self.physical_.writeChunk(fileName, chunkNum, data)
        self.logical_.fileList[fileName].receiveChunk(chunkNum)

    # read serialized state from disk
    def readState(self):
        return self.physical_.readState()

    # write serialized state to disk
    def writeState(self, serializedState):
        self.physical_.writeState(serializedState)

    def serialize(self):
        return self.logical_.serialize()

    ##
    # Private methods
    ##

    def exists(self, fileName):
        return self.logical_.exists(fileName)

