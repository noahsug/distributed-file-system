##
# A node in the distributed p2p file system that runs on a device
##

from network import Network
import error as err
from dfs_state import DFS

class Peer:
    def __init__(self, addr, port):
        self.dfs = DFS(addr, port)
        self.network = Network(self.dfs)

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
        pass

    def delete(self, fileName):
        pass

    def listFiles(self):
        pass

    def pin(self, fileName):
        pass

    def unpin(self, fileName):
        pass

    # enable internet connection
    def connect(self):
        pass

    # disable internet connection
    def disconnect(self):
        pass

    # join DFS, connecting to the peer at the given addr and port
    def join(self, addr, port):
        pass

    def retire(self):
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
