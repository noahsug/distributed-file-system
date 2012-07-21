##
# Creates sockets and listens for new peers that join the DFS.
##

import time

from network_thread import NetworkThread
import dfs_socket

class NewPeerListener(NetworkThread):
    def __init__(self, callback, dfs):
        NetworkThread.__init__(self, dfs)
        self.callback_ = callback

    def startUp(self):
        self.socket_ = dfs_socket.DFSSocket()
        try:
            self.socket_.bind((self.dfs_.addr, self.dfs_.port))
        except Exception, ex:
            self.log_.e('failed to bind: ' + str(ex))
            return

        self.socket_.listen(3)

    def doWork(self):
        try:
            conn, fullAddr = self.socket_.accept()
        except dfs_socket.timeout:
            return
        except Exception, ex:
            self.log_.w('failed to accept: %s', str(ex))
            time.sleep(.1)
            return

        self.callback_(conn)
