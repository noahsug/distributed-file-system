##
# Creates sockets and listens for new peers that join the DFS.
##

import threading
from threading import Thread

class NewPeerListener(Thread):
    def __init__(self):
        Thread.__init__(self)


