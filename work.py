##
# Represents a task that must get done. Work is serialized and sent over the network.
##

UPDATE = 'u'

class Work:
    def __init__(self, type, source, dest, data=None):
        self.type = type # the type of work
        self.source = source # the dfs object of the sender thread
        self.dest = dest # the listener thread on which the data should be sent
        self.data = data # the data to send
