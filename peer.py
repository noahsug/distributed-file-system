#!/usr/bin/python

import Queue
import re
import sets
import socket
import sys
import threading
import time
import os.path

errOK             =  0; # Everything good
errUnknownWarning =  1; # Unknown warning
errUnknownFatal   = -2; # Unknown error
errCannotConnect  = -3; # Cannot connect to anything; fatal error
errNoPeersFound   = -4; # Cannot find any peer (e.g., no peers in a peer file); fatal
errPeerNotFound   =  5; # Cannot find some peer; warning, since others may be connectable

CHUNK_SIZE = 16384

class Connection(threading.Thread):
    PASS = 'p' # let the other peer have a chance to ask for something and update it on our file status
    IDLE = 'i' # there's no more work to be done with the other peer
    CLOSE = 'c' # close the other peer
    FILE = 'f' # send over a file chunk

    def __init__(self, peer):
        self.lock_ = threading.Lock()
        self.peer_ = peer
        threading.Thread.__init__(self)
        self.futureActions = [self.PASS]
        self.active = True # True connection hasn't been closed
        self.initialized = False # True when addr and port are defined
        self.idleSleepTime = .025

    def acquire(self):
        self.lock_.acquire()

    def release(self):
        self.lock_.release()

    def sleep(self):
        time.sleep(self.idleSleepTime)
        if self.idleSleepTime < .5:
            self.idleSleepTime += .025

    def addAction(self, action):
        self.futureActions.append(action)

    def getAction(self):
        action = 0
        self.acquire()
        if len(self.futureActions) == 0:
            action = self.findWork()
        else:
            action = self.futureActions[0]
        self.release()
        return action

    def nextAction(self):
        self.acquire()
        if len(self.futureActions) > 0:
            self.futureActions.pop(0)
        self.release()

    def connect(self, addr, port):
        self.addr = addr
        self.port = port
        self.id = "%s:%d" % (self.addr, self.port)
        self.initialized = True
        self.isReceiver_ = False
        self.socket_ = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            self.socket_.connect((addr, port))
        except Exception as ex:
            DB('DEBUG: ' + self.peer_.id + ' - Cannot connect to peer ' + addr + ' ' + str(port) + ' # ' + str(ex))
            self.active = False
            return errPeerNotFound
        return errOK

    def receive(self, conn):
        # we don't know the port or addr until the connection has been made
        self.addr = ''
        self.port = 0
        self.socket_ = conn
        self.isReceiver_ = True
        return errOK

    def run(self):
        if self.isReceiver_:
            self.initRecveiver()
        else: # we are the connector - send addr and port to start the connection
            self.sendData(self.peer_.id)
        while self.active:
            self.takeRequest()

    def initRecveiver(self):
        data = self.readData()
        if not data:
            DB('DEBUG: ' + 'failed to init receiver')
            self.close()
            return errCannotConnect
        addr, port = data.split(':')
        port = int(port)

        if self.peer_.alreadyHasConnection(addr, port):
            DB(self.peer_.id + ' - closing duplicate connection to ' + addr + ' ' + str(port))
            self.sendData(self.CLOSE)
            self.close()
        else:
            self.addr = addr
            self.port = port
            self.id = "%s:%d" % (self.addr, self.port)
            self.initialized = True
            self.makeRequest()

    def takeRequest(self):
        data = self.readData()
        if not data:
            DB('DEBUG: ' + self.peer_.id + ' - failed to take request')
            self.close()
            return errCannotConnect
        request = data[0] # the first character is the request
        data = data[1:] # the rest is the data
        if len(data) > 60:
            DB(self.peer_.id + ' - RECEIVED a large amount of data from ' + self.id)
        else:
            DB(self.peer_.id + ' - RECEIVED ' + request + data + ' from ' + self.id)

        if request == self.FILE:
            fileName, chunkNum = self.deserializeFileRequest(data)
            chunkData = self.peer_.storage.getChunk(fileName, chunkNum)
            self.sendData(chunkData)

        elif request == self.PASS:
            self.peer_.files.update(self.id, data)
            self.makeRequest()

        elif request == self.IDLE:
            self.peer_.files.update(self.id, data)
            currentAction = self.getAction()
            if (currentAction == self.IDLE):
                DB(self.peer_.id + ' - is sleeping with ' + self.id)
                self.sleep() # reduce how much we spam the network with useless packets
                self.addAction(self.PASS)
                self.makeRequest()
            else:
                self.makeRequest(currentAction)

        elif request == self.CLOSE:
            self.close()

        else:
            DB('DEBUG' + self.peer_.id + ' - received unknown data' + request + data + ' from ' + self.id)

    def makeRequest(self, action='none'):
        if action == 'none':
            action = self.getAction()
        self.nextAction()

        if action[0] == self.FILE:
            self.sendData(action)
            fileName, chunkNum = self.deserializeFileRequest(action[1:])
            chunkData = self.readRawData()
            if not chunkData:
                DB('DEBUG: ' + self.peer_.id + ' - failed to make a request to ' + self.id)
                self.close()
                return errCannotConnect
            numChunks = len(self.peer_.files.files[fileName])
            self.peer_.storage.writeChunk(fileName, chunkNum, chunkData)
            self.peer_.files.markChunkAsRetreived(fileName, chunkNum)
            action = self.PASS

        if action == self.PASS:
            msg = "%s%s" % (self.PASS, self.peer_.files.serialize())
            self.sendData(msg)

        if action == self.IDLE:
            msg = "%s%s" % (self.IDLE, self.peer_.files.serialize())
            self.sendData(msg)

        if action == self.CLOSE:
            self.sendData(self.CLOSE)
            self.close()

        if action != self.CLOSE and action != self.IDLE and action != self.PASS and action != self.FILE:
            DB('DEBUG' + self.peer_.id + ' - has unknown action' + action + ' for ' + self.id)

    def findWork(self):
        chunkInfo = self.peer_.files.getChunkOwnedByPeer(self.id)
        if chunkInfo == FileStatus.NO_CHUNK_FOUND:
            return self.IDLE
        fileName, chunk = chunkInfo
        return '%s%s;%d' % (Connection.FILE, encode(fileName), chunk)

    def readRawData(self):
        data = ''
        try:
            data = self.socket_.recv(CHUNK_SIZE)
        except Exception as ex:
            DB('DEBUG: ' + 'failed to read raw data # ' + str(ex))
            pass

        if data:
            return data
        return ''

    def readData(self):
        data = ''
        try:
            data = self.socket_.recv(CHUNK_SIZE)
        except Exception as ex:
            DB('DEBUG: ' + 'failed to read data # ' + str(ex))
            pass

        if data:
            return repr(data)[1:-1]
        return ''

    def sendData(self, msg):
        try:
            self.socket_.sendall(msg)
        except Exception as ex:
            DB('DEBUG: ' + 'failed to send data # ' + str(ex))
            self.close()

    def deserializeFileRequest(self, text):
        fileName, chunkNum = re.split('(?<!\\\);', text)
        fileName = decode(fileName)
        chunkNum = int(chunkNum)
        return (fileName, chunkNum)

    def close(self):
        self.active = False
        if self.initialized:
            self.peer_.files.removePeer(self.id)
        self.socket_.close()


class Peer:
    def __init__(self, addr, port, peersFile='peers.txt'):
        self.connected = False # becomes true after join() is called
        self.addr = addr
        self.port = port
        self.id = "%s:%d" % (self.addr, self.port)
        self.storage = Storage(port) # Interface to write/read to/from the disk
        self.files = FileStatus(self.storage, self.id) # keeps track of what file chunks we have/need
        self.files.addLocalFiles()
        self.peerConnections = [] # the list of sockets for each peer
        self.peers_ = [] # the list of peers to connect to when join is called
        self.parsePeersFile(peersFile)

    # TODO peersFile should be a filename, not a string that we parse
    def parsePeersFile(self, fileName):
        peersFile = self.storage.readFile(fileName)
        if peersFile == '':
            return
        try:
            line = peersFile.split('\n')
            for peerConnection in line:
                if line == '' or not ' ' in peerConnection:
                    continue
                addr, port = peerConnection.split(' ')
                port = int(port)
                self.peers_.append((addr, port))
        except Exception as ex:
            DB('DEBUG: ' + self.id + ' had an error parsing peers file # ' + str(ex))
            pass

    # API method
    def join(self):
        if self.connected:
            return errOK # already connected, no need to join
        if len(self.peers_) == 0:
            return errNoPeersFound

        self.connected = True
        status = self.listen()
        if status < 0:
            self.connected = False
            return status

        connectedPeers = 0
        failedToConnect = False
        for peer in self.peers_:
            if peer[0] == self.addr and peer[1] == self.port:
                continue # don't connect to youself

            conn = Connection(self)
            status = conn.connect(peer[0], peer[1])
            if status == errPeerNotFound:
                failedToConnect = True
            else:
                conn.start()
                self.peerConnections.append(conn)
                connectedPeers += 1

        if connectedPeers == 0:
            return errNoPeersFound
        if failedToConnect:
            return errPeerNotFound
        return errOK

    # API method
    def insert(self, fileName):
        self.files.addLocalFile(fileName)
        return errOK

    # API method
    def query(self, status):
        fileNames = self.files.files.keys()
        fileNames.sort()
        status.files = [self.files.files[fileName] for fileName in fileNames]
        return errOK

    # API method
    def leave(self):
        if not self.connected:
            return errOK
        self.connected = False

        # stop the listener thread
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((self.addr, self.port)) # connect to self to close to listener thread
        s.close()
        self.listenerThread.join()

        # close all connections to peers
        for conn in self.peerConnections:
            conn.addAction(Connection.CLOSE)
#        for conn in self.peerConnections:
#            conn.join()
#        self.peerConnections = []

        return errOK

    def listen(self):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        try:
            self.socket.bind((self.addr, self.port))
        except Exception as ex:
            DB('DEBUG: ' + self.id + ' - failed to bind socket to ' + self.addr + ':' + str(self.port) + ' # ' + str(ex))
            return errCannotConnect

        self.socket.listen(3)
        self.listenerThread = threading.Thread(target=self.listener)
        self.listenerThread.start()
        return errOK

    def listener(self):
        while self.connected:
            try:
                conn, fullAddr = self.socket.accept()
            except Exception as ex:
                DB('DEBUG: ' + self.id + ' - failed to accept' + ' # ' + str(ex))
                time.sleep(.1)
                continue
            if not self.connected:
                break
            connection = Connection(self)
            connection.receive(conn)
            connection.start()
            self.peerConnections.append(connection)
            DB(self.id + ' established a connection and has ' + str(len(self.peerConnections)) + ' connections total')
        DB(self.id + ' closing listener thread')
        conn.close()

    def alreadyHasConnection(self, addr, port):
        for conn in self.peerConnections:
            if conn.addr == addr and conn.port == port:
                return True
        return False


class FileStatus:
    NO_CHUNK_FOUND = 0
    NO_FILES = 'n'

    def __init__(self, storage, id):
        self.files = {} # mapping of file name to array of chunks
        self.storage_ = storage
        self.lock_ = threading.Lock()
        self.id = id

    def acquire(self):
        self.lock_.acquire()

    def release(self):
        self.lock_.release()

    def addLocalFiles(self):
        for file in self.storage_.getLocalFiles():
            self.addLocalFile(file)

    def addLocalFile(self, filePath):
        fileName = os.path.basename(filePath)
        if fileName in self.files:
            return # file already exists
        self.storage_.copyFileLocally(filePath)
        numChunks = self.storage_.getNumChunks(fileName)
        chunks = [Chunk(Chunk.HAS) for i in range(0, numChunks)]
        self.acquire()
        self.files[fileName] = chunks
        self.release()
        DB(self.id + ' added local file. File status looks like ' + self.serialize())

    def addRemoteFile(self, peer, fileName, maxChunks, chunks):
        self.acquire()
        self.addRemoteFileNoLock(peer, fileName, maxChunks, chunks)
        self.release()

    def addRemoteFileNoLock(self, peer, fileName, maxChunks, chunks):
        if fileName in self.files:
            file = self.files[fileName]
        else:
            file = [Chunk() for i in range(0, maxChunks)]
            self.files[fileName] = file
        for peerOwnedChunk in chunks:
            if peerOwnedChunk < len(file):
                file[peerOwnedChunk].peers.add(peer)
        self.storage_.addEmptyFile(fileName, len(chunks))
        DB(self.id + ' added remote file. File status looks like ' + str(len(self.files[fileName])))

    def markChunkAsRetreived(self, fileName, chunk):
        self.acquire()
        chunk = self.files[fileName][chunk]
        chunk.status = Chunk.HAS
        self.release()

    def removePeer(self, peer):
        self.acquire()
        for fileName in self.files:
            chunks = self.files[fileName]
            for chunk in chunks:
                if peer in chunk.peers:
                    chunk.peers.remove(peer)
                    if chunk.status == Chunk.GETTING and chunk.gettingFrom == peer:
                        chunk.status = Chunk.NEED
        self.release()

    # Looks at all chunks the peer has and returns the least replicated one
    def getChunkOwnedByPeer(self, peer):
        self.acquire()
        bestFileName = ''
        bestChunk = -1
        leastReplication = sys.maxint
        for fileName in self.files:
            chunks = self.files[fileName]
            for i, chunk in enumerate(chunks):
                if chunk.status == Chunk.NEED and peer in chunk.peers:
                    replication = len(chunk.peers)
                    if replication < leastReplication:
                        leastReplication = replication
                        bestFileName = fileName
                        bestChunk = i
                        if replication == 1:
                            self.markChunkAsBeingRetreived(chunk, peer)
                            self.release()
                            return (bestFileName, bestChunk)

        if bestFileName == '' or len(self.files[fileName]) <= bestChunk:
            self.release()
            return self.NO_CHUNK_FOUND

        if chunk.status != Chunk.NEED:
            return self.getFirstChunk(peer)

        self.markChunkAsBeingRetreived(self.files[fileName][bestChunk], peer)
        self.release()
        return (bestFileName, bestChunk)

    def markChunkAsBeingRetreived(self, chunk, peer):
        chunk.status = Chunk.GETTING
        chunk.gettingFrom = peer

    def getFirstChunk(self, peer):
        bestFileName = ''
        bestChunk = -1
        for fileName in self.files:
            for i, chunk in enumerate(self.files[fileName]):
                if chunk.status == Chunk.NEED:
                    return (fileName, i)
        return self.NO_CHUNK_FOUND

    def update(self, peer, data):
        if data == self.NO_FILES:
            return
        files = re.split('(?<!\\\)#', data)
        self.acquire()
        for file in files:
            file = unescape(file)
            fileName, chunkInfo = re.split('(?<!\\\);', file)
            chunkInfo = chunkInfo.split(',')
            fileName = decode(fileName)
            chunks = [int(i) for i in chunkInfo[1:]]
            maxChunks = int(chunkInfo[0])
            self.addRemoteFileNoLock(peer, fileName, maxChunks, chunks)
        self.release()


    # status of what chunks we own: noah.txt;7,1,2,3,5,6#etc.. - "I have chunks 1, 2, 3, 5, 6 of noah.txt which has 7 chunks total"
    def serialize(self):
        text = ''
        first = True
        self.acquire()
        for fileName in self.files:
            chunks = self.files[fileName]
            chunkText = ''
            for i, chunk in enumerate(chunks):
                if chunk.status == Chunk.HAS:
                    chunkText += ',' + str(i)
            if chunkText == '':
                continue
            if not first:
                text += '#'
            else:
                first = False
            text += "%s;%d%s" % (encode(fileName), len(chunks), chunkText)
        self.release()
        if text == '':
            return self.NO_FILES
        return text

class Storage:
    def __init__(self, port):
        self.port = port
        self.lock_ = threading.Lock()
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
            w.write(' ' * size * CHUNK_SIZE) # fill the file with empty space
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
        except Exception as ex:
            DB('DEBUG: failed to readFileNoLock # ' + str(ex))
            return ''
        return text


    def getChunk(self, fileName, chunk):
        self.acquire()
        filePath = os.path.join(self.getPath(), fileName)
        f = open(filePath, 'r')
        f.seek(chunk * CHUNK_SIZE)
        data = f.read((chunk + 1) * CHUNK_SIZE)
        f.close()
        self.release()
        return data

    def writeChunk(self, fileName, chunkNum, data):
        #Assume data is no longer than size CHUNK_SIZE
        self.acquire()
        filePath = os.path.join(self.getPath(), fileName)
        f = open(filePath, "r+")
        f.seek(chunkNum * CHUNK_SIZE)
        f.write(data)

        # Resize the file b/c the last chunk may be smaller then CHUNK_SIZE
        if len(data) < CHUNK_SIZE: # is this the last chunk?
            f.truncate()

        f.close()
        self.release()

    def getNumChunks(self, fileName):
        self.acquire()
        filePath = os.path.join(self.getPath(), fileName)
        size = os.path.getsize(filePath)
        self.release()
        return int(size / CHUNK_SIZE) + 1

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

class Chunk:
    NEED = 'n'
    HAS = 'h'
    GETTING = 'g'

    def __init__(self, status=NEED):
        self.gettingFrom = '' # addr:port of the peer currently transferring this file to us
        self.peers = sets.Set() # set of peers that have this chunk
        self.status = status


class Status:
    def __init__(self):
        self.files = []

    def numFiles(self):
        return len(self.files)

    def fractionPresentLocally(self, fileNum):
        if not self.isValidIndex(fileNum):
            return -1

        presentLocally = 0
        chunks = self.files[fileNum]
        for chunk in chunks:
            if chunk.status == Chunk.HAS:
                presentLocally += 1
        return float(presentLocally) / len(chunks)

    def fractionPresent(self, fileNum):
        if not self.isValidIndex(fileNum):
            return -1

        present = 0
        chunks = self.files[fileNum]
        for chunk in chunks:
            if chunk.status == Chunk.HAS or len(chunk.peers) > 0:
                present += 1
        return float(present) / len(chunks)

    def minimumReplicationLevel(self, fileNum):
        if not self.isValidIndex(fileNum):
            return -1

        min = sys.maxint
        chunks = self.files[fileNum]
        for chunk in chunks:
            level = len(chunk.peers)
            if chunk.status == Chunk.HAS:
                level += 1
            if level < min:
                min = level
        return min

    def averageReplicationLevel(self, fileNum):
        if not self.isValidIndex(fileNum):
            return -1

        total = 0
        chunks = self.files[fileNum]
        for chunk in chunks:
            total += len(chunk.peers)
            if chunk.status == Chunk.HAS:
                total += 1
        return float(total) / len(chunks)

    def isValidIndex(self, i):
        return 0 <= i < len(self.files)


def encode(text):
    return text.replace('\\', '\\\\').replace(';', '\\;').replace('#', '\\#')

def decode(text):
    return text.replace('\\#', '#').replace('\\;', ';').replace('\\\\', '\\')

def unescape(text):
    return text.replace('\\\\', '\\')

# thread safe printing for debugging purposes
dbLock = threading.Lock()
def DB(text):
    dbLock.acquire()
    print text
    dbLock.release()

