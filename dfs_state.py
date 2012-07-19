##
# Keeps track of constants for one instance of the DFS.
##

from identification import ID

class DFS:
    def __init__(self, addr, port):
        self.addr = addr
        self.port = port
        self.id = ID(addr, port)
