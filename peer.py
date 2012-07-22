##
# A node in the distributed p2p file system that runs on a device
##

from network import Network
from file_system import FileSystem
import error as err
from dfs_state import DFS
from base import Base

class Peer(Base):
    def __init__(self, addr, port):
        Base.__init__(self, DFS(addr, port))
        self.network_ = Network(self.dfs_)
        self.fs_ = FileSystem(self.dfs_)

    ##
    # Public API
    ##
    def read(self, fileName, buf, offset, bufsize):
        status = self.updateFile(fileName)
        if status >= 0:
            status = self.fs_.readIntoBuffer(fileName, buf, offset, bufsize)
        return status

    def write(self, fileName, buf, offset, bufsize):
        if self.fs_.exists(fileName):
            self.fs_.write(fileName, buf, offset, bufsize)
        else:
            self.fs_.add(fileName, buf, offset, bufsize)
            self.network_.fileAdded(fileName)
        return err.OK

    def delete(self, fileName):
        self.fs_.delete(fileName)
        self.network_.fileDeleted(fileName)
        return err.OK

    def listFiles(self, files):
        files.fromlist(self.fs_.list())
        return err.OK

    def pin(self, fileName):
        status = self.updateFile(fileName)
        return status

    def unpin(self, fileName):
        self.fs_.deleteLocalCopy(fileName)
        return err.OK

    # join DFS, connecting to the peer at the given addr and port if given
    def join(self, addr, port):
        status = self.network_.join(DFS(addr, port))
        return status

    # retire from the system
    def retire(self):
        return err.OK

    # connect to the internet
    def connect(self):
        self.network_.connect()
        return err.OK

    # disconnect from the internet
    def disconnect(self):
        self.network_.disconnect()
        return err.OK

    def query(self, status):
        return err.OK

    # exits the program
    def exit(self):
        # write system status to disk
        exit()

    ##
    # Private functions
    ##
    def updateFile(self, fileName):
        status = err.OK
        if not self.fs_.isUpToDate(fileName):
            status = network.getFile(self, fileName)
        return status
