##
# Represents the physical view of the DFS.
##

import os.path

import dfs_socket
import error as err
from base import Base
from lock import Lock

shareFolderPath = os.path.expanduser("~/Share/")
saveStateName = '.state'

class PhysicalView(Base):
    def __init__(self, dfs):
        Base.__init__(self, dfs)
        self.lock_ = Lock(dfs)
        self.createBaseFolder()

    def read(self, fileName, buf, offset, bufsize):
        # TODO add thread safetly
        filePath = os.path.join(self.getBasePath(), fileName)
        try:
            f = open(filePath, "r")
        except Exception, ex:
            self.log_.e('error opening file in read mode ' + filePath + ': ' + str(ex))
            return err.FileNotFound

        # TODO return error if offset + bufsize > filesize

        status = err.OK
        f.seek(offset)
        try:
            buf.fromfile(f, bufsize)
        except Exception, ex:
            self.log_.e('failed to read ' + filePath + ' from ' + str(offset) + ' to ' + str(offset + bufsize) + ': ' + str(ex))
            status = err.CannotReadFile
        f.close()
        return status

    ## to do
    def write(self, fileName, buf, offset, bufsize):
        filePath = os.path.join(self.getBasePath(), fileName)
        try:
            f = open(filePath, "w")
        except Exception, ex:
            self.log_.e('error opening file in write mode ' + filePath + ': ' + str(ex))
            return err.FileNotFound

        if offset > self.getFileSize(filePath):
           # increment file size to
           pass

        f.seek(offset)
        f.write(buf)
        f.close()
        return err.OK

    def getChunk(self, fileName, chunk):
        self.lock_.acquire()
        filePath = os.path.join(self.getBasePath(), fileName)
        f = open(filePath, 'r')
        f.seek(chunk * dfs_socket.CHUNK_SIZE)
        data = f.read(dfs_socket.CHUNK_SIZE)
        f.close()
        self.lock_.release()
        return data

    def writeChunk(self, fileName, chunkNum, data):
        # Assume data is no longer than size CHUNK_SIZE
        self.lock_.acquire()
        filePath = os.path.join(self.getBasePath(), fileName)
        f = open(filePath, "r+")
        f.seek(chunkNum * dfs_socket.CHUNK_SIZE)
        f.write(data)

        # Resize the file b/c the last chunk may be smaller then CHUNK_SIZE
        if len(data) < dfs_socket.CHUNK_SIZE: # is this the last chunk?
            f.truncate()

        f.close()
        self.lock_.release()

    def getNumChunks(self, fileName):
        self.lock_.acquire()
        filePath = os.path.join(self.getBasePath(), fileName)
        size = self.getFileSize(filePath, fileName)
        self.lock_.release()
        return int(size / dfs_socket.CHUNK_SIZE) + 1

    def deleteFile(self, fileName):
        self.lock_.acquire()
        os.remove(fileName)
        self.lock_.release()

    def writeState(self, serializedState):
        path = os.path.join(self.getBasePath(), saveStateName)
        self.lock_.acquire()
        f = open(path, 'w')
#        f.write(serializedState)
        f.write('testing 1 2 3')
        f.close()
        self.lock_.release()

    ##
    # Private methods
    ##

    def createBaseFolder(self):
        if not os.path.isdir(shareFolderPath):
            os.mkdir(shareFolderPath)
        if not os.path.isdir(self.getBasePath()):
            os.mkdir(self.getBasePath())

    def getBasePath(self):
        dirName = "peer" + str(self.dfs_.id)
        return shareFolderPath + dirName + "/"

    def fillEmptyFile(self, fileName, size):
        self.lock_.acquire()
        path = os.path.join(self.getBasePath(), fileName)
        if not os.path.isfile(path):
            w = open(path, "w")
            w.write(' ' * size * dfs_socket.CHUNK_SIZE) # fill the file with empty space
            w.close()
        self.lock_.release()

    def getFileSize(self, filePath):
        return os.path.getsize(filePath)
#===============================================================================
#    def copyFileLocally(self, filePath):
#        self.lock_.acquire()
#        newPath = os.path.join(self.getBasePath(), os.path.basename(filePath))
#        if not os.path.isfile(newPath):
#            w = open(newPath, "w")
#            w.write(self.readFileNoLock(filePath))
#            w.close()
#        self.lock_.release()
#
#    def readFile(self, fileName):
#        self.lock_.acquire()
#        text = self.readFileNoLock(fileName)
#        self.lock_.release()
#        return text
#
#    def readFileNoLock(self, fileName):
#        try:
#            f = open(os.path.expanduser(fileName), 'r')
#            text = f.read()
#            f.close()
#        except Exception, _ex:
#            #DB('DEBUG: failed to readFileNoLock # ' + str(_ex))
#            return ''
#        return text
#===============================================================================
