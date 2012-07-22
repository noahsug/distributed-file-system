##
# A node in the distributed p2p file system that runs on a device
##

from network import Network
import error as err
from dfs_state import DFS
from base import Base
from storage import Storage

class Peer(Base):
    def __init__(self, addr, port):
        Base.__init__(self, DFS(addr, port))
        self.network_ = Network(self.dfs_) # handles sending/recieving data to/from other peers
        self.storage_ = Storage(self.dfs_) # handles writing/reading to/from disk
        self.view_ = View(self.dfs_) # manages the logically view

    ##
    # Public API
    ##
    def read(self, fileName, buf, offset, bufsize):
        status = self.updateFile(fileName)
        file = self.storage_.open(fileName, offset)
        try:
            buf.fromfile(file, bufsize)
        except Exception, ex:
            self.log_.e('failed to read ' + fileName + ' from ' + str(offset) + ' to ' + str(offset + bufsize) + ': ' + str(ex))
            status = err.CannotReadFile
        return status

    def write(self, fileName, buf, offset, bufsize):
        if self.isNewFile(fileName):
        self.network_.fileAdded(fileName)
        self.open(fileName, "w")
        pass

    def delete(self, fileName):
        self.view_.deleteFile(fileName)
        self.storage_.deleteFile(fileName)
        self.network_.fileDeleted(fileName)

    def listFiles(self):
        return self.view_.listFiles()

    def pin(self, fileName):
        return self.updateFile()

    def unpin(self, fileName):
        self.storage_.deleteFile(fileName)
        self.view_.localCopyDeleted(fileName)

    # join DFS, connecting to the peer at the given addr and port if given
    def join(self, addr, port):
        self.network_.join(DFS(addr, port))

    # retire from the system
    def retire(self):
        pass

    # connect to the internet
    def connect(self):
        self.network_.connect()

    # disconnect from the internet
    def disconnect(self):
        self.network_.disconnect()
        pass

    def query(self):
        pass

    # exits the program
    def exit(self):
        # write system status to disk
        exit()

    ##
    # Private functions
    ##
    def updateFile(self, fileName):
        status = err.OK
        if not self.view_.existsLocally(fileName):
            status = network.getFile(self, fileName)
        return status

    def open(self, fileName, op):
        if not self.view_.existsLocally(fileName):
            #if file does not exist locally, get file then open
            self.log_.d("file does not exist locally, pull")
            self.network_.getFile(fileName, self.file_state.fileList[fileName].chunksOwned)

        self.f = open(fileName, op)

    def close(self, fileName):
        self.f.close()
