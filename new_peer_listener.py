##
# Creates sockets and listens for new peers that join the DFS.
##

from threading import Thread
import socket

import peer
from debug import Logger

class NewPeerListener(Thread):
    print debug
    log = Logger('NewPeerListener')

    def __init__(self, callback):
        Thread.__init__(self)
        self.callback = callback
        self.active = True

    def run(self):
        self.socket_ = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket_.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        try:
            self.socket_.bind((peer.addr, peer.port))
        except Exception, ex:
            log.e('failed to bind: %s', str(ex))
            return

        self.socket_.listen(3)
        self.listenForNewPeers()

    def close(self):
        self.active = False
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket_.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.connect((peer.addr, peer.port))
        s.close()

    def listenForNewPeers(self):
        while self.active:
            try:
                conn, fullAddr = self.socket_.accept()
            except Exception, ex:
                log.w('failed to accept: %s', str(ex))
                time.sleep(.1)
                continue

            if not self.active:
                conn.close()
                break

            callback(conn)
