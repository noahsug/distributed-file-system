##
# A node in the distributed p2p file system that runs on a device
##
import time

from network import Network
import error as err
from dfs_state import DFS
from base import Base
import serializer
from file_system import FileSystem

class Peer(Base):
    def __init__(self, addr, port, network=None):
        Base.__init__(self, DFS(addr, port))
        self.fileSystem_ = FileSystem(self.dfs_)

        if not network:
            network = Network(self.dfs_, self.fileSystem_)
        self.network_ = network

# TODO not loading state for now
#        self.loadState()

    ##
    # Public API
    ##
    def open(self, fileName, op):
        exists = self.fileSystem_.exists(fileName)

        if exists and self.fileSystem_.isDeleted(fileName):
            self.log_.i('WARNING: Trying to open non-existant file ' + fileName + ' in "r". Aborting open...')
            return err.CannotOpenFile

        status = self.updateFile(fileName)
        self.log_.i('Opening ' + fileName + ' in "' + op + '"...')

        if op is "r":
            if exists and not self.fileSystem_.physical_.exists(fileName):
                self.log_.i('WARNING: Unable to reteived ' + fileName + '. Aborting open...')
                return err.CannotOpenFile

            if exists:
                if self.fileSystem_.canRead(fileName):
                    self.fileSystem_.logical_.fileList_[fileName].readCounter += 1
                    self.fileSystem_.logical_.fileList_[fileName].state = "r"
                else:
                    self.log_.i('WARNING: Trying to open ' + fileName + ' in "r", but it is already open in "w". Aborting open...')
                    return err.CannotOpenFile
            else:
                self.log_.i('WARNING: Trying to open non-existant file ' + fileName + ' in "r". Aborting open...')
                self.log_.w('tried to open ' + fileName + ' in read mode, but it doesnt exist')
                return err.FileNotFound
        elif op is "w":
            if not exists:
                buf = [' ']
                self.fileSystem_.physical_.fillEmptyFile(fileName, 1)
                self.fileSystem_.add(fileName)
                self.log_.v('creating ' + fileName + ' b/c opened it in write mode for the first time')
            if self.fileSystem_.canWrite(fileName):
                if not self.fileSystem_.physical_.exists(fileName):
                    self.fileSystem_.physical_.fillEmptyFile(fileName, 1)
                self.fileSystem_.logical_.fileList_[fileName].state = "w"
            else:
                self.log_.i('WARNING: Trying to open ' + fileName + ' in "w", but it is already open. Aborting open...')
                return err.CannotOpenFile
        else:
            self.log_.i('WARNING: Trying to open ' + fileName + ' in unknown mode "' + op + '". Aborting open...')
            return err.InvalidOp

        self.log_.v('-- opened ' + fileName + ' in ' + op)
        return status

    def close(self, fileName, noLogging=False):
        if not self.fileSystem_.exists(fileName) or self.fileSystem_.isDeleted(fileName):
            self.log_.i('WARNING: Trying to close non-existant file ' + fileName + ' in "r". Aborting close...')
            self.log_.w('tried to close ' + fileName + ', which doesnt exist: ' + str(self.fileSystem_.exists(fileName)))
            return err.FileNotFound

        file = self.fileSystem_.logical_.fileList_[fileName]
        if file.state is "":
            self.log_.i('WARNING: Trying to close ' + fileName + ', but it is already closed. Aborting close...')
            return err.FileNotOpen

        if not noLogging:
            self.log_.i('Closing ' + fileName + '...')

        if file.state is "r":
            if file.readCounter > 0:
                file.readCounter -= 1
                if file.readCounter == 0:
                    file.state = ''
            else:
                file.state = ""
        else: # state is 'w'
            if file.hasLocalChanges and self.dfs_.online:
                file.latestVersion = file.localVersion.copy()
                self.network_.fileEdited()
                self.network_.waitForPropagation()
            file.state = ""

        self.log_.v('-- closed ' + fileName + ', state is now: ' + file.state)
        return err.OK

    def read(self, fileName, buf=None, offset=0, bufsize=-1):
        if not self.fileSystem_.exists(fileName):
            self.log_.i('WARNING: Unable to retreive ' + fileName + '. Aborting read...')
            self.log_.w('tried to read from ' + fileName + ', which doesnt exist')
            return err.FileNotFound

        if self.fileSystem_.logical_.fileList_[fileName].state is "r":
            if not self.fileSystem_.physical_.exists(fileName):
                self.log_.i('WARNING: Unable to retrieve ' + fileName + '. Aborting read...')
                self.log_.e('tried to read from ' + fileName + ', which doesnt exist physically')
                return err.FileNotFound

            if self.fileSystem_.isMissingChunks(fileName):
                self.log_.i('WARNING: ' + fileName + ' was not fully retreived. You are reading a partially downloaded file.')
            elif self.fileSystem_.logical_.getFile(fileName).isOutOfDate():
                self.log_.i('WARNING: ' + fileName + ' could not be retreived from the system. You are reading an out of date file.')

            if not buf:
                buf = [0] * self.fileSystem_.physical_.getFileSize(fileName)
            if bufsize < 0:
                bufsize = len(buf)
            status = self.fileSystem_.readIntoBuffer(fileName, buf, offset, bufsize)
        else:
            self.log_.i('WARNING: Cannot read from ' + fileName + ' because it is not in read mode. Aborting read....')
            self.log_.w('tried to read from ' + fileName + ' while not in read mode')
            return err.FileNotOpen

        try:
            text = ''.join(buf)
        except Exception:
            text = str(buf)
        textToPrint = text
        if len(textToPrint) > 500:
            textToPrint = textToPrint[:500]
        self.log_.i('Read ' + fileName + ':\n"""\n' + textToPrint + '\n"""')
        return text

    def getSize(self, fileName):
        if self.fileSystem_.physical_.exists(fileName):
            return self.fileSystem_.physical_.getFileSize(fileName)
        return 0

    def hasLocalCopy(self, fileName):
        if not self.fileSystem_.exists(fileName):
            return False
        return self.fileSystem_.isMissingChunks(fileName) or not self.fileSystem_.isUpToDate(fileName)

    def write(self, fileName, buf, offset=0, bufsize=-1, deleteOriginalContent=False):
        if bufsize < 0:
            bufsize = len(buf)

        self.log_.i('Writing buffer of size ' + str(bufsize) + ' to ' + fileName + '...')
        if not self.fileSystem_.exists(fileName):
            self.log_.i('WARNING: Cannot write to ' + fileName + ' because it is not in write mode. Aborting write....')
            return err.FileNotFound

        if self.fileSystem_.logical_.fileList_[fileName].state is "w":
            if deleteOriginalContent:
                self.fileSystem_.physical_.trim(fileName, 1)
            self.fileSystem_.write(fileName, buf, offset, bufsize)
        else:
            self.log_.i('WARNING: Cannot write to ' + fileName + ' because it is not in write mode. Aborting write....')
            self.log_.w('tried to write to ' + fileName + ' while not in write mode')
            return err.FileNotOpenForWrite
        return err.OK

    def delete(self, fileName):
        if not self.fileSystem_.exists(fileName) or self.fileSystem_.isDeleted(fileName):
            self.log_.w(fileName + ' doest exist or is already deleted')
            return 1
        file = self.fileSystem_.logical_.getFile(fileName)
        if file.state != '':
            self.close(fileName, noLogging=True)

        self.log_.i('Deleting ' + fileName + '...')
        self.fileSystem_.delete(fileName)
        self.network_.fileEdited()
        self.network_.waitForPropagation()
        return err.OK

    def listFiles(self, files=[]):
        while len(files) > 0:
            files.pop()
        for f in self.fileSystem_.list():
            files.append(f)
        self.printInfo(files)
        return err.OK

    # mark the file as stable
    def markStable(self, fileName):
        if not self.fileSystem_.exists(fileName):
            self.log_.w('tried to mark ' + fileName + ' as stable, but doesnt exist')
            return 1
        self.log_.i('Marking ' + fileName + ' as stable...')
        newFileName = fileName + ".stable";
        while self.fileSystem_.exists(newFileName):
            newFileName = newFileName + ".stable"
        self.fileSystem_.copyFile(fileName, newFileName)
        if self.dfs_.online:
            self.network_.fileEdited()
            self.network_.waitForPropagation()

    # save the most recent version of the file locally
    def pin(self, fileName):
        if not self.fileSystem_.exists(fileName):
            return err.FileNotFound
        # TODO check write / read access
        self.log_.i('Pinning ' + fileName + '...')
        status = self.updateFile(fileName)
        return status

    # delete the local copy of the file
    def unpin(self, fileName):
        if not self.fileSystem_.exists(fileName):
            return err.FileNotFound
        # TODO check write / read access
        self.log_.i('Unpinning ' + fileName + '...')
        self.fileSystem_.deleteLocalCopy(fileName)
        return err.OK

    # join DFS, connecting to the peer at the given addr and port if given
    def join(self, addr, port=None):
        if not port:
            peer = addr
            addr = peer.dfs_.addr
            port = peer.dfs_.port

        self.log_.i('Connecting to DFS from starting point ' + addr + ':' + str(port) + '...')
        status = self.network_.connectTo(DFS(addr, port))
        self.network_.waitForPropagation()
        return status

    # retire from the system
    def retire(self):
        self.log_.i('Retiring...')
        self.goOffline()
        return err.OK

    # connect to the internet
    def goOnline(self):
        if not self.dfs_.online:
            self.log_.i('Going online...')
            self.network_.connect()
            self.dfs_.online = True
            self.network_.waitForPropagation()
            return err.OK
        else:
            return err.AlreadyOnline

    # disconnect from the internet
    def goOffline(self):
        if self.dfs_.online:
            self.log_.i('Going offline...')
            self.network_.disconnect()
            self.dfs_.online = False
            self.network_.waitForPropagation()
            return err.OK
        else:
            return err.AlreadyOffline

    # exits the program
    def exit(self):
        self.log_.i('exiting...')
        self.goOffline()
        fs = self.fileSystem_.getState()
        ns = self.network_.getState()
        self.log_.v('writing ' + str(len(fs)) + ' files and ' + str(len(ns)) + ' peers to disk')
        state = (fs, ns)
        s = serializer.serialize(state)
        self.fileSystem_.writeState(s)

    ##
    # Private functions
    ##
    def loadState(self):
        state = self.fileSystem_.readState()
        if state:
            try:
                fs, ns = serializer.deserialize(state)
            except Exception, ex:
                self.log_.e('found state, but failed to deserialize: ' + str(ex))
                return

            if len(fs) + len(ns) > 0:
                self.log_.i('Loaded ' + str(len(fs)) + ' files and ' + str(len(ns)) + ' device addresses from state')
                self.fileSystem_.loadFromState(fs)
                self.network_.loadFromState(ns)

    def updateFile(self, fileName):
        status = err.OK
        if not self.fileSystem_.exists(fileName):
            return status

        if self.fileSystem_.isMissingChunks(fileName) or not self.fileSystem_.isUpToDate(fileName):
            status = self.network_.getFile(fileName, 3)

        return status

    def printInfo(self, files):
        self.log_.i('Files:')
        files = sorted(files, key = lambda file: str(file))
        for f in files:
            if not f.isDeleted:
                self.log_.i('  ' + str(f))
