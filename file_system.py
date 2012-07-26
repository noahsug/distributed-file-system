##
# Manages the peers local files.
##

from base import Base
from version import Version
from physical_view import PhysicalView
from logical_view import LogicalView
import error as err
import random
from lock import Lock

class FileSystem(Base):
    def __init__(self, dfs):
        Base.__init__(self, dfs)
        self.physical_ = PhysicalView(dfs)
        self.logical_ = LogicalView(dfs)
        self.updateLock_ = Lock(dfs)

    ##
    # Public API
    ##
    def loadFromState(self, state):
        self.logical_.update(state)

    def list(self):
        return self.logical_.getFileList()

    # returns data from a random chunk from the given list of chunks
    def getRandomChunk(self, fileName, chunks):
        self.updateLock_.acquire()
        if not self.exists(fileName) or not self.isUpToDate(fileName):
            self.updateLock_.release()
            return None

        missing = []
        file = self.logical_.getFile(fileName)
        for i, hasChunk in enumerate(chunks):
            if not hasChunk and file.chunksOwned[i]:
                missing.append(i)

        self.log_.v('Their chunks status: ' + str(chunks))
        self.log_.v('My chunk status: ' + str(file.chunksOwned))
        self.log_.v('Resulting options: ' + str(missing))

        if len(missing) == 0:
            self.updateLock_.release()
            return None

        chunkNum = missing[random.randint(0, len(missing) - 1)]

        if file.localVersion.numChunks <= chunkNum:
            self.log_.e('requested random chunk of ' + fileName + ', but chunk ' + str(chunkNum) + ' >= ' + str(file.numChunks))
            self.updateLock_.release()
            return None
        if not file.chunksOwned[chunkNum]:
            self.log_.e('requested random chunk of ' + fileName + ', but chunk ' + str(chunkNum) + ' is not owned!')
            self.updateLock_.release()
            return None

        chunkData = self.physical_.getChunk(fileName, chunkNum)
        if not chunkData:
            self.updateLock_.release()
            return None

        self.updateLock_.release()
        return (fileName, chunkNum, chunkData)

    def getMissingChunks(self, fileName):
        self.updateLock_.acquire()
        file = self.logical_.getFile(fileName)
        if file.latestVersion.numChunks == file.numChunksOwned:
            self.updateLock_.release()
            return None
        val = self.logical_.fileList_[fileName].chunksOwned
        self.updateLock_.release()
        self.log_.d(str(self.logical_.fileList_[fileName]) + ' - getting missing chunks')
        self.log_.d(fileName + ' owns these chunks: ' + str(val))
        return val

    def canRead(self, fileName):
        return self.logical_.fileList_[fileName].state is "" or self.logical_.fileList_[fileName].state is "r"

    def canWrite(self, fileName):
        return self.logical_.fileList_[fileName].state is not "w"

    def readIntoBuffer(self, fileName, buf, offset, bufsize):
        status = self.physical_.read(fileName, buf, offset, bufsize)
        if not self.logical_.getFile(fileName).isOutOfDate():
            return status
        else:
            self.log_.v('read ' + fileName + ', which is out of date')
            return err.FileOutOfDate

    # adds file to the logical view
    def add(self, fileName, fileSize=None):
        if self.physical_.exists(fileName):
            if fileSize != None:
                self.log_.e('adding ' + fileName + ' and specified file size, but already exists locally!')
            self.logical_.add(fileName, self.physical_.getFileSize(fileName))
            self.logical_.getFile(fileName).ownAllChunks()
        else:
            self.logical_.add(fileName, fileSize)

    def delete(self, fileName):
        self.logical_.delete(fileName)
        if self.physical_.exists(fileName):
            self.physical_.deleteFile(fileName)

    def deleteLocalCopy(self, fileName):
        file = self.logical_.getFile(fileName)
        file.localVersion = file.latestVersion.copy()
        file.ownNoChunks()
        self.physical_.deleteFile(fileName)

    def isUpToDate(self, fileName):
        file = self.logical_.getFile(fileName)
        return file.localVersion == file.latestVersion

    def write(self, fileName, buf, offset, bufsize):
        file = self.logical_.fileList_[fileName]
        if file.state != 'w':
            self.log_.e('writing to ' + fileName + ' while not in write mode!')

        if file.isOutOfDate() or not file.existsLocally(): # conflict, create a second version
            self.log_.v(fileName + ' is being written to and is out of date. Conflict detected.')
            fileName = self.resolveConflict(fileName)

        file = self.logical_.fileList_[fileName]
        self.physical_.write(fileName, buf, offset, bufsize)
        size = self.physical_.getFileSize(fileName)
        v = file.localVersion.getUpdatedVersion(size, self.dfs_.id.str)
        file.localVersion = v
        file.ownAllChunks()
        if self.dfs_.online:
            # if we're online, we update both latest and local b/c our changes will propagate immediatly
            file.latestVersion = v.copy()

        return err.OK

    def writeChunk(self, fileName, chunkNum, data):
        self.updateLock_.acquire()
        file = self.logical_.fileList_[fileName]
        if file.chunksOwned[chunkNum]:
            self.log_.v('got chunk ' + str(chunkNum) + ' of ' + fileName + ', but we already have it')
            self.updateLock_.release()
            return # already has chunk

        if not self.physical_.exists(fileName):
            self.physical_.fillEmptyFile(fileName, file.latestVersion.fileSize)

        self.physical_.writeChunk(fileName, chunkNum, data)
        file.receiveChunk(chunkNum)
        self.updateLock_.release()

    def updateFiles(self, files):
        status = err.OK
        self.updateLock_.acquire()
        for file in files.values():
            if not self.exists(file.fileName):
                if file.isDeleted:
                    continue
                self.add(file.fileName, file.latestVersion.fileSize)
                self.logical_.getFile(file.fileName).setNewVersion(file.latestVersion)
                self.log_.v(file.fileName + ' has been CREATED during an update: size ' + str(file.latestVersion.fileSize))

            localFile = self.logical_.getFile(file.fileName)
            if file.isDeleted and not localFile.isDeleted:
                localFile.isDeleted = True
                self.log_.v(localFile.fileName + ' has been DELETED during an update')
                continue

            if file.latestVersion == localFile.latestVersion and file.hasLocalChanges():
                # file from a peer that just connected, propagate its local changes
                file.latestVersion = file.localVersion.copy()

            if localFile.hasLocalChanges() and localFile.isOutOfDate(file):
                # we made local changes while offline and another peer also made changes, conflict!
                self.resolveConflict(file.fileName)
                localFile = self.logical_.getFile(file.fileName)
                self.log_.v(file.fileName + ' has local changes and is out of date. Conflict detected during update.')
                status = err.CausedConflict

            if localFile.isOutOfDate(file):
                if localFile.latestVersion.numEdits == file.latestVersion.numEdits:
                    self.log_.w(localFile.fileName + ' have same # of edits, yet is out of date')
                self.log_.v('updated ' + localFile.fileName)
                if localFile.numChunksOwned > 0:
                    self.log_.v(file.fileName + ' has out of date local data, only latest is being updated')
                    localFile.latestVersion = file.latestVersion.copy()
                else:
                    localFile.setNewVersion(file.latestVersion.copy())

        for file in self.list():
            if file.hasLocalChanges():
                # while we were offline we were the only ones to make changes, propagate them now
                file.latestVersion = file.localVersion.copy()
                self.log_.v(file.fileName + ' has valid local changes after an update. Now propagating')

        self.updateLock_.release()
        return status

    def copyFile(self, name, newName):
        self.physical_.copyFile(name, newName)
        self.add(newName)
        old = self.logical_.getFile(name)
        new = self.logical_.getFile(newName)

    def beginLocalUpdate(self, fileName):
        self.updateLock_.acquire()
        self.logical_.beginLocalUpdate(fileName)
        self.updateLock_.release()

    def finishLocalUpdate(self, fileName):
        self.updateLock_.acquire()
        file = self.logical_.fileList_[fileName]
        if file.numChunksOwned > 0:
            file.localVersion = file.latestVersion.copy()

        if file.latestVersion.numChunks == file.numChunksOwned:
            self.physical_.trim(fileName, file.latestVersion.fileSize)
            self.updateLock_.release()
            return err.OK

        self.log_.v('failed to fully update ' + fileName + ': only got ' +
                    str(file.numChunksOwned) + '/' + str(file.localVersion.numChunks))
        self.updateLock_.release()
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

    def isMissingChunks(self, fileName):
        file = self.logical_.getFile(fileName)
        return file.numChunksOwned < file.localVersion.numChunks

    ##
    # Private methods
    ##
    def resolveConflict(self, fileName):
        conflictName = fileName + '.' + self.dfs_.id.str
        while self.physical_.exists(conflictName):
            conflictName = conflictName + "." + self.dfs_.id.str

        self.log_.i('WARNING: A conflict was detected with ' + fileName + '. Moving local changes to a new version called ' + conflictName + '.')

        oldState = self.logical_.getFile(fileName).state
        oldReadCounter = self.logical_.getFile(fileName).readCounter

        self.physical_.copyFile(fileName, conflictName)
        self.add(conflictName)
        self.deleteLocalCopy(fileName)

        self.logical_.getFile(conflictName).state = oldState
        self.logical_.getFile(conflictName).readCounter = oldReadCounter
        self.logical_.getFile(fileName).state = ''
        self.logical_.getFile(fileName).readCounter = 0

        return conflictName

