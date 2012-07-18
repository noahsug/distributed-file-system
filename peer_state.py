##
# Keeps track of which peers are part of the DFS
##

import threading

class PeerState:
    def __init__(self):
        self.lock_ = threading.Lock()
