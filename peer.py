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
    def __init__(self, addr, port):
        Base.__init__(self, DFS(addr, port))
        self.fileSystem_ = FileSystem(self.dfs_)
        self.network_ = Network(self.dfs_, self.fileSystem_)
        self.loadState()

    ##
    # Public API
    ##
    def open(self, fileName, op):
        status = self.updateFile(fileName)
        exists = self.fileSystem_.logical_.exists(fileName)
        
        if op is "r":
            if exists:
                if self.fileSystem_.canRead(fileName):
                    self.fileSystem_.logical_.fileList_[fileName].readCounter = self.fileSystem_.logical_.fileList_[fileName].readCounter + 1
                    self.fileSystem_.logical_.fileList_[fileName].state = "r"
                else:
                    return err.CannotOpenFile
            else:
                return err.FileNotFound
        elif op is "w":
            if not self.fileSystem_.logical_.exists(fileName):
                buf = [' ']
                self.fileSystem_.physical_.write(fileName, buf, 0, 1)
                self.fileSystem_.logical_.add(fileName, self.fileSystem_.physical_.getFileSize(fileName), self.fileSystem_.physical_.getNumChunks(fileName))
            
            if self.fileSystem_.canWrite(fileName):
                self.fileSystem_.logical_.fileList_[fileName].state = "w"
        else:
            return err.CannotOpenFile
        return status

    def close(self, fileName):
        if self.fileSystem_.logical_.fileList_[fileName].state is "":
            return err.FileNotOpen
        elif self.fileSystem_.logical_.fileList_[fileName].state is "r":
            if self.fileSystem_.logical_.fileList_[fileName].readCounter > 0:
                self.fileSystem_.logical_.fileList_[fileName].readCounter = self.fileSystem_.logical_.fileList_[fileName].readCounter - 1
            else:
                self.fileSystem_.logical_.fileList_[fileName].state = ""
        else:
            self.network_.fileEdited()
            self.fileSystem_.logical_.fileList_[fileName].state = ""
        return err.OK

    def read(self, fileName, buf, offset, bufsize):
        if self.fileSystem_.logical_.fileList_[fileName].state is "r":
            status = self.fileSystem_.readIntoBuffer(fileName, buf, offset, bufsize)
        else:
            return err.FileNotOpen
        return status

    def write(self, fileName, buf, offset, bufsize):
        if self.fileSystem_.logical_.fileList_[fileName].state is "w":
            self.fileSystem_.write(fileName, buf, offset, bufsize)
            version = self.fileSystem_.getVersion(fileName)
        else:
            return err.FileNotOpenForWrite
        return err.OK

    def delete(self, fileName):
        self.log_.v('delete ' + fileName)
        self.fileSystem_.delete(fileName)
        self.network_.fileEdited()
        return err.OK

    def listFiles(self, files):
        self.log_.v('listFiles')
        files.fromlist(self.fileSystem_.list())
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
        self.log_.v('pin')
        status = self.updateFile(fileName)
        return status

    # delete the local copy of the file
    def unpin(self, fileName):
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
        if not self.fileSystem_.isUpToDate(fileName):
            status = self.network_.getFile(self, fileName)
        return status
