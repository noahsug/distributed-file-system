##
# A node in the distributed p2p file system that runs on a device
##

from network import Network
from file_system import FileSystem
import error as err
from dfs_state import DFS
from base import Base
import serializer

class Peer(Base):
    def __init__(self, addr, port):
        Base.__init__(self, DFS(addr, port))
        self.network_ = Network(self.dfs_)
        self.fileSystem_ = FileSystem(self.dfs_)
        self.loadState()

    ##
    # Public API
    ##
    def open(self, fileName, op):
        pass

    def close(self, fileName):
        pass

    def read(self, fileName, buf, offset, bufsize):
        status = self.updateFile(fileName)
        if status >= 0:
            status = self.fileSystem_.readIntoBuffer(fileName, buf, offset, bufsize)
        return status

    def write(self, fileName, buf, offset, bufsize):
        self.fileSystem_.write(fileName, buf, offset, bufsize)
        version = self.fileSystem_.getVersion(fileName)
        return err.OK

    def delete(self, fileName):
        self.fileSystem_.delete(fileName)
        self.network_.fileDeleted(fileName)
        return err.OK

    def listFiles(self, files):
        files.fromlist(self.fileSystem_.list())
        return err.OK

    # mark the file as stable
    def stable(self, fileName):
        pass

    # save the most recent version of the file locally
    def pin(self, fileName):
        status = self.updateFile(fileName)
        return status

    # delete the local copy of the file
    def unpin(self, fileName):
        self.fileSystem_.deleteLocalCopy(fileName)
        return err.OK

    # join DFS, connecting to the peer at the given addr and port if given
    def join(self, addr, port):
        status = self.network_.join(DFS(addr, port))
        return status

    # retire from the system
    def retire(self):
        self.disconnect()
        return err.OK

    # connect to the internet
    def connect(self):
        self.network_.connect()
        self.dfs_.online = True
        return err.OK

    # disconnect from the internet
    def disconnect(self):
        self.network_.disconnect()
        self.dfs_.online = False
        return err.OK

    def query(self, status):
        return err.OK

    # exits the program
    def exit(self):
        fs = self.fileSystem_.serialize()
        nw = self.network_.serialize()
        state = (fs, nw)
        s = serializer.serialize(state)
        self.fileSystem_.writeState(s)
        exit()

    ##
    # Private functions
    ##
    def loadState(self):
        state = self.fileSystem_.readState()
        if state:
            try:
                fs, nw = serializer.deserialize(state)
            except Exception, ex:
                self.log_.e('found state, but failed to deserialize: ' + str(ex))
                return
            self.fileSystem_.loadFromState(fs)
            self.network_.loadFromState(nw)
            self.log_.v('successfully loaded states')

    def updateFile(self, fileName):
        status = err.OK
        if not self.fileSystem_.isUpToDate(fileName):
            status = self.network_.getFile(self, fileName)
        return status
