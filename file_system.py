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
            self.log_.v('read ' + fileName + ', which is out of date')
            return err.FileOutOfDate

    # adds file to the logical view
    def add(self, fileName, fileSize=None):
        if self.physical_.exists(fileName):
            self.logical_.add(fileName, self.physical_.getFileSize(fileName))
        else:
            self.logical_.add(fileName, fileSize)

    def delete(self, fileName):
        self.logical_.delete(fileName)
        self.physical_.deleteFile(fileName)

    def deleteLocalCopy(self, fileName):
        self.physical_.deleteFile(fileName)

    def isUpToDate(self, fileName):
        return self.logical_.fileList_[fileName].localVersion.equals(self.logical_.fileList_[fileName].latestVersion)

    def write(self, fileName, buf, offset, bufsize):
        file = self.logical_.fileList_[fileName]
        if file.state != 'w':
            self.log_.e('writing to ' + fileName + ' while not in write mode!')

        if file.isOutOfDate(): # conflict, create a second version
            self.log_.v(fileName + ' is being written to and is out of date. Conflict detected.')
            conflictName = self.resolveConflict(fileName)
            self.physical_.write(conflictName, buf, offset, bufsize)

        self.physical_.write(fileName, buf, offset, bufsize)
        size = self.physical_.getFileSize(fileName)
        v = file.localVersion.getUpdatedVersion(size, self.dfs_.id)
        file.localVersion = v
        if self.dfs_.online:
            # if we're online, we update both latest and local b/c our changes will propagate immediatly
            file.latestVersion = v.copy()

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
            if not self.exists(file.fileName):
                self.add(file.fileName, file.latestVersion.fileSize)
                self.logical_.getFile(file.fileName).setNewVersion(file.latestVersion)
                self.log_.v(file.fileName + ' has been CREATED during an update')
                continue

            localFile = self.logical_.getFile(file.fileName)
            if file.isDeleted and not localFile.isDeleted: # deleted?
                localFile.isDeleted = True
                self.log_.v(localFile.fileName + ' has been DELETED during an update')
                continue

            if file.latestVersion == localFile.latestVersion and file.hasLocalChanges():
                # file from a peer that just connected, propagate its local changes
                file.latestVersion = file.localVersion.copy()

            if localFile.hasLocalChanges() and localFile.isOutOfDate(file):
                # we made local changes while offline and another peer also made changes, conflict!
                self.resolveConflict(file.fileName)
                newVersionOfLocalFile = localFile
                newVersionOfLocalFile.latestVersion = file.latestVersion.copy()
                self.log_.v(localFile.fileName + ' has local changes and is out of date. Conflict detected during update.')
                status = err.CausedConflict

            elif localFile.hasLocalChanges():
                # while we were offline we were the only ones to make changes, propagate them now
                localFile.latestVersion = localFile.localVersion.copy()

        return status

    def beginLocalUpdate(self, fileName):
        self.deleteLocalCopy(self, fileName)
        self.logical_.beginLocalUpdate(fileName)

    def finishLocalUpdate(self, fileName):
        file = self.logical_.fileList_[fileName]
        if file.existsLocally():
            file.localVersion = file.latestVersion.copy()
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

    def isDeleted(self, fileName):
        return self.logical_.getFile(fileName).isDeleted

    def copyFile(self, name, newName):
        self.physical_.copyFile(name, newName)
        self.add(newName)
        old = self.logical_.getFile(name)
        new = self.logical_.getFile(newName)
        new.localVersion = old.localVersion.copy()
        new.latestVersion = old.latestVersion.copy()
        new.numChunksOwned = old.numChunksOwned
        new.chunksOwned = list(old.chunksOwned)

    ##
    # Private methods
    ##
    def resolveConflict(self, fileName):
        conflictName = fileName + '.' + self.dfs_.id.str
        while self.physical_.exists(conflictName):
            conflictName = conflictName + "." + self.dfs_.id.str

        self.copyFile(fileName, conflictName)
        self.moveMode(self.logical_.getFile(fileName), self.logical_.getFile(conflictName))
        return conflictName

    def moveMode(self, t, f):
        t.state = f.state
        f.state = ''

