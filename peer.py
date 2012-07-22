##
# A node in the distributed p2p file system that runs on a device
##

from network import Network
import error as err
from dfs_state import DFS
from base import Base

class Peer(Base):
    def __init__(self, addr, port):
        Base.__init__(self, DFS(addr, port))
        self.network_ = Network(self.dfs_)

    ##
    # Public API
    ##
    def open(self, fileName, op):
        pass

    def close(self, fileName):
        pass

    def read(self, fileName, buf, offset, bufsize):
        pass

    def write(self, fileName, buf, offset, bufsize):
        self.network_.fileAdded(fileName)

    def delete(self, fileName):
        pass

    def listFiles(self):
        pass

    def pin(self, fileName):
        pass

    def unpin(self, fileName):
        pass

    # join DFS, connecting to the peer at the given addr and port if given
    def join(self, addr, port):
        self.network_.join(DFS(addr, port))

    # retire from the system
    def retire(self):
        pass

    # connect to the internet
    def connect(self):
        self.network_.connect()

    # disconnect from the internet
    def disconnect(self):
        self.network_.disconnect()
        pass

    def query(self):
        pass

    # exits the program
    def exit(self):
        # write system status to disk
        exit()

    ##
    # Private functions
    ##
