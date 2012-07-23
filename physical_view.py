##
# Represents the physical view of the DFS.
##

import os.path

import dfs_socket
from base import Base
from lock import Lock

shareFolderPath = os.path.expanduser("~/Share/")

class PhysicalView(Base):
    def __init__(self, dfs):
        Base.__init__(self, dfs)
        self.lock_ = Lock(dfs)
        self.createBaseFolder()

    def createBaseFolder(self):
        if not os.path.isdir(shareFolderPath):
            os.mkdir(shareFolderPath)
        if not os.path.isdir(self.getBasePath()):
            os.mkdir(self.getBasePath())

    def getBasePath(self):
        dirName = "peer" + str(self.dfs_.id)
        return shareFolderPath + dirName + "/"

    def copyFileLocally(self, filePath):
        self.acquire()
        newPath = os.path.join(self.getPath(), os.path.basename(filePath))
        if not os.path.isfile(newPath):
            w = open(newPath, "w")
            w.write(self.readFileNoLock(filePath))
            w.close()
        self.release()

    def readFile(self, fileName):
        self.acquire()
        text = self.readFileNoLock(fileName)
        self.release()
        return text

    def readFileNoLock(self, fileName):
        try:
            f = open(os.path.expanduser(fileName), 'r')
            text = f.read()
            f.close()
        except Exception, _ex:
            #DB('DEBUG: failed to readFileNoLock # ' + str(_ex))
            return ''
        return text

    def getLocalFiles(self):
        self.acquire()
        fileList = []
        path = self.getPath()
        if os.path.isdir(path):
            for localFile in os.listdir(path):
                localFilePath = os.path.join(path, localFile)
                if os.path.isfile(localFilePath):
                    fileList.append(localFilePath)
        self.release()
        return fileList

    def getNumChunks(self, fileName):
        self.acquire()
        filePath = os.path.join(self.getPath(), fileName)
        size = os.path.getsize(filePath)
        self.release()
        return int(size / dfs_socket.CHUNK_SIZE) + 1

    def fillEmptyFile(self, fileName, size):
        self.acquire()
        path = os.path.join(self.getPath(), fileName)
        if not os.path.isfile(path):
            w = open(path, "w")
            w.write(' ' * size * dfs_socket.CHUNK_SIZE) # fill the file with empty space
            w.close()
        self.release()
        
    def getChunk(self, fileName, chunk):
        self.acquire()
        filePath = os.path.join(self.getPath(), fileName)
        f = open(filePath, 'r')
        f.seek(chunk * dfs_socket.CHUNK_SIZE)
        data = f.read(dfs_socket.CHUNK_SIZE)
        f.close()
        self.release()
        return data

    def write(self, fileName, buf, offset, bufsize):
        pass

    def writeChunk(self, fileName, chunkNum, data):
        #Assume data is no longer than size CHUNK_SIZE
        self.acquire()
        filePath = os.path.join(self.getPath(), fileName)
        f = open(filePath, "r+")
        f.seek(chunkNum * dfs_socket.CHUNK_SIZE)
        f.write(data)

        # Resize the file b/c the last chunk may be smaller then CHUNK_SIZE
        if len(data) < dfs_socket.CHUNK_SIZE: # is this the last chunk?
            f.truncate()

        f.close()
        self.release()

    def deleteFile(self, fileName):
        self.acquire()
        os.remove(fileName)
        self.release()

    def readIntoBuffer(self, fileName, buf, offset, bufsize):
        # TODO add thread safetly
        status = err.OK
        open(fileName, offset)
        try:
            buf.fromfile(file, bufsize)
        except Exception, ex:
            self.log_.e('failed to read ' + fileName + ' from ' + str(offset) + ' to ' + str(offset + bufsize) + ': ' + str(ex))
            status = err.CannotReadFile
        close(fileName)
        return status
