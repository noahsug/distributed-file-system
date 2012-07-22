##
# Represents a task that must get done. Work is serialized and sent over the network.
##

HANDSHAKE = 'hs'

class Work:
    def __init__(self, type, source, dest, data=None):
        self.type = type
        self.source = source
        self.dest = dest
        self.data = data
