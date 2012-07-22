##
# Each listening thread is pairs with one peer. It listens for data and
# requests and updates the sending thread with new work to do.
# Acts as a slave to the sender thread.
##

from network_thread import NetworkThread
import dfs_state
import dfs_socket
import error as err

class ListenerThread(NetworkThread):
    def __init__(self, dfs, callback):
        NetworkThread.__init__(self, dfs)
        self.callback_ = callback
        self.data_ = ''

    def connect(self, dfs):
        self.connDFS_ = dfs

        self.socket_ = dfs_socket.DFSSocket()
        try:
            self.socket_.connect((self.connDFS_.addr, self.connDFS_.port))
        except Exception, ex:
            self.log_.w('cannot connect to ' + str(self.connDFS_.id) + ': ' + str(ex))
            self.close()
            return err.CannotConnect
        return err.OK

    def setConnection(self, conn):
        self.connDFS_ = dfs_state.NullDFS
        self.socket_ = conn

    def sendData(self, data):
        if not self.active_:
            return err.NotActive
        try:
            self.socket_.sendall(data)
        except Exception, ex:
            self.log_.w('cannot send data to ' + str(self.connDFS_.id) + ': ' + str(ex))
            self.close()
            return err.CannotConnect
        return err.OK

    def doWork(self):
        while not self.receivedAllData():
            try:
                #            data = self.socket_.recv(dfs_socket.CHUNK_SIZE)
                self.data_ = self.socket_.recv(10)
            except dfs_socket.timeout:
                return
            except Exception, ex:
                self.log_.w('cannot recv from ' + str(self.connDFS_.id) + ': ' + str(ex))
                self.close()
                return

        if self.data_:
            self.log_.v('received: ' + data)
#            self.callback_(data)

    def receivedAllData(self):
        return True
#        len(self.data_) < len(dfs_socket.DATA_END)

    def tearDown(self):
        self.socket_.close()
