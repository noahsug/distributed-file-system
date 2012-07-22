import os.path

import dfs_socket
from base import Base
from lock import Lock
from file import File
from file_state import FileState

class Storage(Base):
    
    shareFolderPath = os.path.expanduser("~/Share/")

    def __init__(self, dfs):
        Base.__init__(self, dfs)
        self.lock_ = Lock(dfs)
        self.dfs = dfs
        self.file_state = FileState(self.dfs_)
        self.fileList = {}

        if not os.path.isdir(Storage.shareFolderPath):
            os.mkdir(Storage.shareFolderPath)

        if not os.path.isdir(self.getPath()):
            os.mkdir(self.getPath())

    def acquire(self):
        self.lock_.acquire()

    def release(self):
        self.lock_.release()

    def getPath(self):
        dirName = "peer" + self.dfs.id
        return Storage.shareFolderPath + dirName + "/"

    def addEmptyFile(self, fileName, size):
        self.acquire()
        path = os.path.join(self.getPath(), fileName)
        if not os.path.isfile(path):
            w = open(path, "w")
            w.write(' ' * size * dfs_socket.CHUNK_SIZE) # fill the file with empty space
            w.close()
        self.release()

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
        size = os.path.getsize(filePath)
        self.release()
        return int(size / dfs_socket.CHUNK_SIZE) + 1

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
    
    def addFile(self, fileName, numChunks):
        self.acquire()
        f = File(fileName, numChunks, self.dfs_.id)
        self.fileList[fileName] = f
        self.release()
    
    def deleteFile(self, fileName):
        self.acquire()
        del self.fileList[fileName]
        if(os.path.isdir(fileName)):
            os.removedirs(fileName)
            for key in self.fileList.iterkeys():
                if fileName in key:
                    del self.fileList[key]
        elif(os.path.isfile(fileName)):
            os.remove(fileName)
        self.release()

    def editMade(self, fileName, editor='self'):
        pass

    def hasConflict(self, fileName, numEdits):
        pass
    
    def serializeStateToDisk(self):
        pass

    def deserializeStateFromDisk(self):
        pass
