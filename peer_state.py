##
# Serializable object that contains a list of peers in the system
##

class PeerState():
    def __init__(self, peers=[]):
        self.peers = peers

