import dfs_socket
from lock import Lock
import os.path

class Storage:
    def __init__(self, port):
        self.port = port
        self.lock_ = Lock(tag='storage')
        dirName = "peer" + str(self.port)
        if not os.path.isdir(os.path.expanduser("~/Share/")):
            os.mkdir(os.path.expanduser("~/Share/"))

        if not os.path.isdir(self.getPath()):
            os.mkdir(self.getPath())

    def acquire(self):
        self.lock_.acquire()

    def release(self):
        self.lock_.release()

    def getPath(self):
        dirName = "peer" + str(self.port)
        return os.path.expanduser("~/Share/" + dirName + "/")

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
        except Exception, ex:
            #DB('DEBUG: failed to readFileNoLock # ' + str(ex))
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
    
    def serializeStateToDisk(self):
        pass
        
    def deserializeStateFromDisk(self):
        pass