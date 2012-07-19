##
# A node in the distributed p2p file system that runs on a device
##

from system_state import dfs
from network import Network
import error as err

class Peer:
    def __init__(self, addr, port):
        dfs.addr = addr
        dfs.port = port
        dfs.id.init(addr, port)
        self.network = Network()

    ##
    # Public API
    ##
    def open(fileName, op):
        pass

    def close(fileName):
        pass

    def read(fileName, buf, offset, bufsize):
        pass

    def write(fileName, buf, offset, bufsize):
        pass

    def delete(fileName):
        pass

    def listFiles():
        pass

    def pin(fileName):
        pass

    def unpin(fileName):
        pass

    # enable internet connection
    def connect():
        pass

    # disable internet connection
    def disconnect():
        pass

    # join DFS, connecting to the peer at the given addr and port
    def join(addr, port):
        pass

    def retire():
        pass

    def query():
        pass

    # exits the program
    def exit():
        # write system status to disk
        exit()

    ##
    # Private functions
    ##
