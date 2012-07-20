##
# Creates sockets and listens for new peers that join the DFS.
##

from threading import Thread
import time

from base import Base
import socket, dfs_socket

class NewPeerListener(Base, Thread):

    def __init__(self, callback, dfs):
        Thread.__init__(self)
        Base.__init__(self, dfs)
        self.callback_ = callback
        self.active_ = True

    def run(self):
        self.socket_ = dfs_socket.DFSSocket()
        try:
            self.socket_.bind((self.dfs_.addr, self.dfs_.port))
        except Exception, ex:
            self.log_.e(('failed to bind: %s', str(ex)))
            return

        self.socket_.listen(3)
        self.listenForNewPeers()

    def close(self):
        self.active_ = False

    def listenForNewPeers(self):
        while self.active_:
            try:
                conn, fullAddr = self.socket_.accept()
            except socket.timeout:
                continue
            except Exception, ex:
                self.log_.w('failed to accept: %s', str(ex))
                time.sleep(.1)
                continue

            self.callback_(conn)
