##
# Keeps track of which peers are part of the DFS
##

from base import Base
from lock import Lock

class PeerState(Base):
    def __init__(self, dfs):
        Base.__init__(self, dfs)
        self.lock_ = Lock(dfs)
        self.peers_ = []

    def addPeer(self, dfs):
        self.peers_.append(dfs)
