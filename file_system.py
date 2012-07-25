##
# Manages the peers local files.
##

from base import Base
from version import Version
from physical_view import PhysicalView
from logical_view import LogicalView
import error as err
import random

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

    # returns data from a random chunk from the given list of chunks
    def getRandomChunk(self, fileName, chunks):
        if not self.exists(fileName) or not self.isUpToDate(fileName):
            return None

        missing = []
        for i, hasChunk in enumerate(chunks):
            if not hasChunk:
                missing.append(i)

        chunkNum = missing[random.randint(0, len(missing))]
        chunkData = self.physical_.getChunk(fileName, chunkNum)
        return (fileName, chunkNum, chunkData)

    def getMissingChunks(self, fileName):
        return self.logical_.fileList_[fileName].chunksOwned

    def canRead(self, fileName):
        return self.logical_.fileList_[fileName].state is "" or self.logical_.fileList_[fileName].state is "r"

    def canWrite(self, fileName):
        return self.logical_.fileList_[fileName].state is not "w"

    def readIntoBuffer(self, fileName, buf, offset, bufsize):
        status = self.physical_.read(fileName, buf, offset, bufsize)
        if self.isUpToDate(fileName):
            return status
        else:
            return err.FileOutOfDate

    def add(self, fileName, numChunks):
        if self.physical_.exists(fileName):
            self.logical_.add(fileName, self.physical_.getFileSize(fileName), numChunks)
        else:
            self.logical_.add(fileName, 0, 0)

    def delete(self, fileName):
        self.logical_.delete(fileName)
        self.physical_.deleteFile(fileName)

    def deleteLocalCopy(self, fileName):
        self.physical_.deleteFile(fileName)

    def isUpToDate(self, fileName):
        return self.logical_.fileList_[fileName].localVersion.equals(self.logical_.fileList_[fileName].latestVersion)

    def write(self, fileName, buf, offset, bufsize):
        if self.isUpToDate(fileName): #if up to date, no conflicts
            self.physical_.write(fileName, buf, offset, bufsize)
            ver = Version(fileName, self.logical_.getLocalVersion(fileName).numEdits + 1, self.physical_.getNumChunks(fileName), self.physical_.getFileSize(fileName), self.dfs_.id)
            self.logical_.setNewVersion(fileName, ver)
            return err.OK
        elif self.logical_.fileList_[fileName].localVersion.isOutOfDate(self.logical_.fileList_[fileName].latestVersion): #local < latest, conflict (update failed)
            conflictName = self.resolveConflict(fileName)
            self.physical_.write(conflictName, buf, offset, bufsize)
            self.add(conflictName, self.physical_.getNumChunks(conflictName))
            return conflictName
        else: #local > latest, offline edits
            self.physical_.write(fileName, buf, offset, bufsize)
            self.logical_.setLocalVersion(fileName, self.logical_.getLatestVersion(fileName).numEdits + 1, self.physical_.getNumChunks(fileName), self.physical_.getFileSize(fileName), self.dfs_.id)
            return err.OK

    def writeChunk(self, fileName, chunkNum, data):
        if self.logical_.fileList_[fileName].chunksOwned[chunkNum]:
            return # already has chunk

        if not self.physical_.exists(fileName):
            self.physical_.fillEmptyFile(fileName, self.logical_.fileList_[fileName].latestVersion.fileSize)

        self.physical_.writeChunk(fileName, chunkNum, data)
        self.logical_.fileList_[fileName].receiveChunk(chunkNum)

    def updateFiles(self, files):
        status = err.OK
        # TODO make threadsafe
        for file in files.values():
            if file not in self.logical_.fileList_: # new file?
                self.add(file.fileName, file.latestVersion.numChunks)

            localFile = self.logical_.fileList_[file.fileName]
            if file.isDeleted: # deleted?
                localFile.isDeleted = True

            if localFile.hasLocalChanges() and localFile.isOutOfDate(file): # conflict?
                conflictName = self.resolveConflict(file.fileName)
                self.add(conflictName, self.physical_.getNumChunks(conflictName))
                status = err.CausedConflict
        return status

    def beginLocalUpdate(self, fileName):
        self.deleteLocalCopy(self, fileName)
        self.logical_.beginLocalUpdate(fileName)

    def finishLocalUpdate(self, fileName):
        file = self.logical_.fileList_[fileName]
        if file.existsLocally():
            file.localVersion = file.latestVersion
            return err.OK
        else:
            self.log_.v('failed to fully update ' + fileName + ': only got ' +
                        str(file.numChunksOwned) + '/' + str(file.numChunksTotal))
            return err.CannotFullyUpdateFile

    # read serialized state from disk
    def readState(self):
        return self.physical_.readState()

    # write serialized state to disk
    def writeState(self, serializedState):
        self.physical_.writeState(serializedState)

    def getState(self):
        return self.logical_.getState()

    def exists(self, fileName):
        return self.logical_.exists(fileName)

    ##
    # Private methods
    ##

    def resolveConflict(self, fileName):
        conflictName = fileName + '.' + self.dfs_.id
        while self.physical_.exists(conflictName):
            conflictName = conflictName + "." + self.dfs_.id

        self.physical_.copyFile(fileName, conflictName)
        return conflictName

