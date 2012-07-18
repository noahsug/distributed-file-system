##
# Creates sockets and listens for new peers that join the DFS.
##

import threading
from threading import Thread
import socket

import peer

import debug
import Log from debug

class NewPeerListener(Thread):
    log = Logger('NewPeerListener')

    def __init__(self):
        Thread.__init__(self)
        self.socket_ = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            self.socket_.connect((peer.addr, peer.port))
        except Exception, ex:
            log.e('Cannot connect to peer: %s', str(ex))
            self.active = False
            return errPeerNotFound


