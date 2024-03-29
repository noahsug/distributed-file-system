##
# Keeps track of constants for one instance of the DFS.
##

from identification import ID

CHUNK_SIZE = 65536

class DFS:
    def __init__(self, addr='', port=10000):
        self.addr = addr
        self.port = port
        self.id = ID(addr, port)
        self.online = False

    def init(self, addr, port):
        self.__init__(addr, port)

    def isInit(self):
        return self.addr != ''

    def __hash__(self):
        return self.id.str.__hash__()

    def __eq__(self, other):
        return self.__hash__() == other.__hash__()

    def __ne__(self, other):
        return not self.__eq__(other)

NullDFS = DFS()
