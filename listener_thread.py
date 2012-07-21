##
# Each listening thread is pairs with one peer. It listens for data and
# requests and updates the sending thread with new work to do.
# Acts as a slave to the sender thread.
##

from network_thread import NetworkThread
import dfs_socket

class ListenerThread(NetworkThread):
    def connect(self, dfs):
        self.connDFS_ = dfs
        self.socket_ = dfs_socket.DFSSocket()
        try:
            self.socket_.connect((self.connDFS_.addr, self.connDFS_.port))
        except Exception, ex:
            self.log_.w('peer ' + str(self.connDFS_.id) + ' not found: ' + str(ex))
            self.close()

    def setConnection(self, conn):
        pass

    def getConn(self):
        return self.socket_

    def tearDown(self):
        self.socket_.close()
