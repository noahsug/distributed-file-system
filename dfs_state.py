##
# Keeps track of constants for one instance of the DFS.
##

from identification import ID

class DFS:
    def __init__(self, addr='', port=10000):
        self.addr = addr
        self.port = port
        self.id = ID(addr, port)
        self.online = False

    def init(self, addr, port):
        self.__init__(addr, port)

    def __hash__(self):
        return self.id.str.__hash__()

    def equals(self, other):
        return self.__hash__() == other.__hash__()

    def isInit(self):
        return self.addr != ''

NullDFS = DFS()
