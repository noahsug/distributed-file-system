##
# A node in the distributed p2p file system that runs on a device
##

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

        self.loadState()

    ##
    # Public API
    ##
    def open(self, fileName, op):
        status = self.updateFile(fileName)
        exists = self.fileSystem_.exists(fileName)

        if op is "r":
            if exists:
                if self.fileSystem_.canRead(fileName):
                    self.fileSystem_.logical_.fileList_[fileName].readCounter += 1
                    self.fileSystem_.logical_.fileList_[fileName].state = "r"
                else:
                    self.log_.w('cant open ' + fileName + ' in read mode')
                    return err.CannotOpenFile
            else:
                self.log_.w('tried to open ' + fileName + ' in read mode, but it doesnt exist')
                return err.FileNotFound
        elif op is "w":
            if not exists:
                buf = [' ']
                self.fileSystem_.physical_.fillEmptyFile(fileName, 1)
                self.fileSystem_.add(fileName, 1)
                self.log_.v('creating ' + fileName + ' b/c opened it in write mode for the first time')
            if self.fileSystem_.canWrite(fileName):
                self.fileSystem_.logical_.fileList_[fileName].state = "w"
            else:
                self.log_.w('cant open ' + fileName + ' in write mode')
                return err.CannotOpenFile
        else:
            self.log_.w('tried to open in known mode ' + op)
            return err.InvalidOp

        self.log_.v('opened ' + fileName + ' in ' + op)
        return status

    def close(self, fileName):
        if not self.fileSystem_.exists(fileName):
            self.log_.w('tried to close ' + fileName + ', which doesnt exist')
            return err.FileNotFound

        file = self.fileSystem_.logical_.fileList_[fileName]
        if file.state is "":
            self.log_.v('tried to closed ' + fileName + ', but it was already closed')
            return err.FileNotOpen
        elif file.state is "r":
            if file.readCounter > 0:
                file.readCounter -= 1
            else:
                file.state = ""
        else: # state is 'w'
            if file.hasLocalChanges:
                file.latestVersion = file.localVersion
                self.network_.fileEdited()
            else:
                self.log_.v(fileName + ' closed in write mode, but has no local changes')
            file.state = ""

        self.log_.v('closed ' + fileName + ', state is now: ' + file.state)
        return err.OK

    def read(self, fileName, buf, offset, bufsize):
        self.log_.v('read ' + fileName)
        if not self.fileSystem_.exists(fileName):
            self.log_.w('tried to read from ' + fileName + ', which doesnt exist')
            return err.FileNotFound

        if self.fileSystem_.logical_.fileList_[fileName].state is "r":
            status = self.fileSystem_.readIntoBuffer(fileName, buf, offset, bufsize)
        else:
            self.log_.w('tried to read from ' + fileName + ' while not in read mode')
            return err.FileNotOpen
        return status

    def write(self, fileName, buf, offset, bufsize):
        self.log_.v('write ' + fileName)
        if not self.fileSystem_.exists(fileName):
            return err.FileNotFound

        if self.fileSystem_.logical_.fileList_[fileName].state is "w":
            self.fileSystem_.write(fileName, buf, offset, bufsize)
        else:
            self.log_.w('tried to write to ' + fileName + ' while not in write mode')
            return err.FileNotOpenForWrite
        return err.OK

    def delete(self, fileName):
        self.log_.v('delete ' + fileName)
        self.fileSystem_.delete(fileName)
        self.network_.fileEdited()
        return err.OK

    def listFiles(self, files):
        self.log_.v('listFiles')
        while len(files) > 0:
            files.pop()
        for f in self.fileSystem_.list():
            files.append(f)
        self.printInfo(files)
        return err.OK

    # mark the file as stable
    def markStable(self, fileName):
        self.log_.v('mark stable ' + fileName)
        newFileName = fileName + ".stable";
        while self.fileSystem_.exists(newFileName):
            newFileName = newFileName + ".stable"

        self.fileSystem_.physical_.copyFile(fileName, newFileName)
        self.fileSystem_.add(newFileName, self.fileSystem_.physical_.getNumChunks(newFileName))

    # save the most recent version of the file locally
    def pin(self, fileName):
        self.log_.v('pin ' + fileName)
        if not self.fileSystem_.exists(fileName):
            return err.FileNotFound

        self.log_.v('pin')
        status = self.updateFile(fileName)
        return status

    # delete the local copy of the file
    def unpin(self, fileName):
        self.log_.v('unpin ' + fileName)
        if not self.fileSystem_.exists(fileName):
            return err.FileNotFound

        self.log_.v('unpin')
        self.fileSystem_.deleteLocalCopy(fileName)
        return err.OK

    # join DFS, connecting to the peer at the given addr and port if given
    def join(self, addr, port):
        self.log_.v('join')
        status = self.network_.connectTo(DFS(addr, port))
        return status

    # retire from the system
    def retire(self):
        self.log_.v('retire')
        self.goOffline()
        return err.OK

    # connect to the internet
    def goOnline(self):
        if not self.dfs_.online:
            self.log_.v('go online')
            self.network_.connect()
            self.dfs_.online = True
            return err.OK
        else:
            return err.AlreadyOnline

    # disconnect from the internet
    def goOffline(self):
        if self.dfs_.online:
            self.log_.v('go offline')
            self.network_.disconnect()
            self.dfs_.online = False
            return err.OK
        else:
            return err.AlreadyOffline

    def query(self, status):
        return err.OK

    # exits the program
    def exit(self):
        self.log_.v('exit')
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
            self.fileSystem_.loadFromState(fs)
            self.network_.loadFromState(ns)

    def updateFile(self, fileName):
        status = err.OK
        if not self.fileSystem_.exists(fileName):
            return status
        if not self.fileSystem_.isUpToDate(fileName):
            status = self.network_.getFile(fileName)
        return status

    def printInfo(self, files):
        self.log_.v('-- Files')
        for f in files:
            self.log_.v(str(f))
        self.log_.v('-- / end files')
