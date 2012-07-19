##
# Keeps track of which peers are part of the DFS
##

from lock import Lock

class PeerState:
    def __init__(self):
        self.lock_ = Lock('PeerState')
