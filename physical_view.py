##
# Represents the physical view of the DFS.
##

import os.path
import shutil

import dfs_state
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
            data = f.read(bufsize)
            for i, d in enumerate(data):
                buf[i] = d
        except Exception, ex:
            self.log_.e('failed to read ' + filePath + ' from ' + str(offset) + ' to ' + str(offset + bufsize) + ': ' + str(ex))
            status = err.CannotReadFile
        f.close()
        return status

    def write(self, fileName, buf, offset, bufsize):
        status = err.OK
        size = self.getFileSize(fileName)
        f = open(os.path.join(self.getBasePath(), fileName), "r+")
        if(offset > size):
            f.seek(0, 2)
            f.write(' ' * (offset - size))

        f.seek(offset)
        try:
            for i in range(bufsize):
                f.write(buf[i])
        except Exception, ex:
            self.log_.e('failed to write ' + fileName + ' from ' + str(offset) + ' to ' + str(offset + bufsize) + ': ' + str(ex))
            status = err.CannotReadFile
        f.close()
        return status

    def getChunk(self, fileName, chunk):
        filePath = os.path.join(self.getBasePath(), fileName)
        self.lock_.acquire()
        try:
            f = open(filePath, 'r')
        except Exception, ex:
            self.log_.e('getChunk - failed to open ' + filePath)
            return None

        data = None
        try:
            f.seek(chunk * dfs_state.CHUNK_SIZE)
            data = f.read(dfs_state.CHUNK_SIZE)
        except Exception, ex:
            self.log_.e('getChunk - failed to seek to chunk ' + chunk + ' in ' + filePath)
        f.close()
        self.lock_.release()
        return data

    def writeChunk(self, fileName, chunkNum, data):
        # Assume data is no longer than size CHUNK_SIZE
        self.lock_.acquire()
        filePath = os.path.join(self.getBasePath(), fileName)
        f = open(filePath, "r+")
        f.seek(chunkNum * dfs_state.CHUNK_SIZE)
        f.write(data)

        # Resize the file b/c the last chunk may be smaller then CHUNK_SIZE
        if len(data) < dfs_state.CHUNK_SIZE: # is this the last chunk?
            f.truncate()

        f.close()
        self.lock_.release()

    def getNumChunks(self, fileName):
        self.lock_.acquire()
        size = self.getFileSize(fileName)
        self.lock_.release()
        return int(size / dfs_state.CHUNK_SIZE) + 1

    def copyFile(self, src, des):
        self.lock_.acquire()
        shutil.copyfile(os.path.join(self.getBasePath(), src), os.path.join(self.getBasePath(), des))
        self.lock_.release()

    def deleteFile(self, fileName):
        self.lock_.acquire()
        os.remove(os.path.join(self.getBasePath(), fileName))
        self.lock_.release()

    def writeState(self, serializedState):
        path = os.path.join(self.getBasePath(), saveStateName)
        self.lock_.acquire()
        f = open(path, 'w')
        f.write(serializedState)
        f.close()
        self.log_.v('writing state to disk at ' + path)
        self.lock_.release()

    def readState(self):
        path = os.path.join(self.getBasePath(), saveStateName)
        if not os.path.exists(path):
            return None
        self.lock_.acquire()
        f = open(path, 'r')
        state = f.read()
        f.close()
        self.lock_.release()
        return state

    ##
    # Private methods
    ##

    def createBaseFolder(self):
        if not os.path.isdir(shareFolderPath):
            os.mkdir(shareFolderPath)
        if not os.path.isdir(self.getBasePath()):
            os.mkdir(self.getBasePath())

    def exists(self, fileName):
        return os.path.exists(os.path.join(self.getBasePath(), fileName))

    def getBasePath(self):
        dirName = "peer_" + str(self.dfs_.id)
        return shareFolderPath + dirName + "/"

    def fillEmptyFile(self, fileName, size):
        self.lock_.acquire()
        path = os.path.join(self.getBasePath(), fileName)
        if not os.path.isfile(path):
            w = open(path, "w")
            w.write(' ' * size) # fill the file with empty space
            w.close()
        self.lock_.release()

    def getFileSize(self, fileName):
        return os.path.getsize(os.path.join(self.getBasePath(), fileName))
