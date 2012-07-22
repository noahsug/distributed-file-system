##
# Keeps track of constants for one instance of the DFS.
##

from identification import ID

class DFS:
    def __init__(self, addr='', port=10000):
        self.addr = addr
        self.port = port
        self.id = ID(addr, port)

    def init(self, addr, port):
        self.__init__(addr, port)

NullDFS = DFS()
