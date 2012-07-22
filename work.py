##
# Represents a task that must get done. Work is serialized and sent over the network.
##

HANDSHAKE = 0

class Work:
    def __init__(self, type, data=None):
        self.type = type
        self.data = data
