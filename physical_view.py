##
# Represents the physical view of the DFS.
##

import os.path

import dfs_socket
import error as err
from base import Base
from lock import Lock

shareFolderPath = os.path.expanduser("~/Share/")

class PhysicalView(Base):
    def __init__(self, dfs):
        Base.__init__(self, dfs)
        self.lock_ = Lock(dfs)
        self.createBaseFolder()
        
    def read(self, fileName, buf, offset, bufsize):
        # TODO add thread safetly
        status = err.OK
        f = open(fileName, "r")
        f.seek(offset)
        try:
            buf.fromfile(f, bufsize)
        except Exception, ex:
            self.log_.e('failed to read ' + fileName + ' from ' + str(offset) + ' to ' + str(offset + bufsize) + ': ' + str(ex))
            status = err.CannotReadFile
        f.close()
        return status

    ## to do
    def write(self, fileName, buf, offset, bufsize):
        status = err.OK
        f = open(fileName, "w")
        
        if(offset + bufsize > self.getFileSize(os.path.join(self.getPath(), fileName)):
           # increment file size to
           pass
        
        f.seek(offset)
        try:
            f.write()
        
    def getChunk(self, fileName, chunk):
        self.acquire()
        filePath = os.path.join(self.getPath(), fileName)
        f = open(filePath, 'r')
        f.seek(chunk * dfs_socket.CHUNK_SIZE)
        data = f.read(dfs_socket.CHUNK_SIZE)
        f.close()
        self.release()
        return data

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

    def getNumChunks(self, fileName):
        self.acquire()
        filePath = os.path.join(self.getPath(), fileName)
        size = self.getFileSize(os.path.join(self.getPath(), fileName))
        self.release()
        return int(size / dfs_socket.CHUNK_SIZE) + 1

    def deleteFile(self, fileName):
        self.acquire()
        os.remove(fileName)
        self.release()

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
        self.acquire()
        path = os.path.join(self.getPath(), fileName)
        if not os.path.isfile(path):
            w = open(path, "w")
            w.write(' ' * size * dfs_socket.CHUNK_SIZE) # fill the file with empty space
            w.close()
        self.release()
        
    def getFileSize(self, fileName):
        return os.path.getsize(fileName)
#===============================================================================
#    def copyFileLocally(self, filePath):
#        self.acquire()
#        newPath = os.path.join(self.getPath(), os.path.basename(filePath))
#        if not os.path.isfile(newPath):
#            w = open(newPath, "w")
#            w.write(self.readFileNoLock(filePath))
#            w.close()
#        self.release()
# 
#    def readFile(self, fileName):
#        self.acquire()
#        text = self.readFileNoLock(fileName)
#        self.release()
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

