##
# Each listening thread is pairs with one peer. It listens for data and
# requests and updates the sending thread with new work to do.
# Acts as a slave to the sender thread.
##

from network_thread import NetworkThread
import dfs_state
import dfs_socket
import error as err
import serializer

class ListenerThread(NetworkThread):
    def __init__(self, dfs, callback):
        NetworkThread.__init__(self, dfs)
        self.callback_ = callback
        self.connDFS_ = dfs_state.NullDFS
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
        self.socket_ = conn

    def getConnDFS(self):
        return self.connDFS_

    def sendWork(self, work):
        if not self.active_:
            return err.NotActive
        try:
            data = self.package(work)
            self.socket_.sendall(data)
        except Exception, ex:
            self.log_.w('cannot send data to ' + str(self.connDFS_.id) + ': ' + str(ex))
            self.close()
            return err.CannotConnect
        return err.OK

    def doWork(self):
        while not self.receivedAllData():
            try:
                data = self.socket_.recv(4096)
            except dfs_socket.timeout:
                self.data_ = ''
                return
            except Exception, ex:
                self.log_.w('cannot recv from ' + str(self.connDFS_.id) + ': ' + str(ex))
                self.close()
                return

            if not data:
                self.log_.v('connection with ' + str(self.connDFS_.id) + ' was closed')
                self.close()
                return

            self.data_ += data

        if self.data_:
            work = self.unpackage(self.data_)
            if work:
                self.callback_(work)
            self.data_ = ''

    def receivedAllData(self):
        terminatorLen = len(dfs_socket.DATA_TERMINATOR)
        if len(self.data_) < terminatorLen:
            return False
        return self.data_[-terminatorLen:] == dfs_socket.DATA_TERMINATOR

    def package(self, work):
        work.dest = None
        data = serializer.serialize(work)
        data += dfs_socket.DATA_TERMINATOR
        return data

    def unpackage(self, data):
        terminatorLen = len(dfs_socket.DATA_TERMINATOR)
        data = data[-terminatorLen:]
        try:
            work = serializer.deserialize(data)
        except Exception, ex:
            self.log_.e('failed to deserialize work')
            return None
        work.dest = self
        self.updateDFS(work.source)
        return work

    def updateDFS(self, dfs):
        if not self.connDFS_.isInit() and dfs.isInit():
            self.connDFS_ = dfs

    def tearDown(self):
        self.socket_.close()

