#!/usr/bin/python

import Queue
import re
import sets
import socket
import sys
import threading
import time

errOK             =  0; # Everything good
errUnknownWarning =  1; # Unknown warning
errUnknownFatal   = -2; # Unknown error
errCannotConnect  = -3; # Cannot connect to anything; fatal error
errNoPeersFound   = -4; # Cannot find any peer (e.g., no peers in a peer file); fatal
errPeerNotFound   =  5; # Cannot find some peer; warning, since others may be connectable

CHUNK_SIZE = 65536

class Connection(threading.Thread):
    IDLE = 'i'
    UPDATE = 'u'
    CLOSE = 'c'

    def __init__(self, peer):
        self.peer_ = peer
        threading.Thread.__init__(self)
        self.actions = [self.UPDATE]

    def addAction(self, action):
        self.actions.append(action)

    def getAction(self):
        if len(self.actions) == 0:
            return self.IDLE
        return self.actions[0]

    def connect(self, addr, port):
        self.active = False # false when the connection is closed
        self.addr = addr
        self.port = port
        self.id = "%s:%d" % (self.addr, self.port)
        self.isReceiver_ = False
        self.socket_ = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try :
            self.socket_.connect((addr, port))
            self.active = True
        except:
            print 'DEBUG:', self.peer_.id, '- Cannot connect to peer', addr, port
            return errPeerNotFound
        return errOK

    def receive(self, conn):
        self.active = True
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
            self.socket_.sendall(self.peer_.id)

        while self.active:
            self.takeRequest()

    def initRecveiver(self):
        data = self.socket_.recv(CHUNK_SIZE)
        data = repr(data)
        addr, port = data[1:-1].split(':')
        port = int(port)

        if self.peer_.alreadyHasConnection(addr, port):
            print self.peer_.id, '- closing duplicate connection to', addr, port
            self.socket_.sendall(self.CLOSE)
            self.socket_.close()
            self.active = False
        else:
            self.addr = addr
            self.port = port
            self.id = "%s:%d" % (self.addr, self.port)
            self.sendRequest()

    def takeRequest(self):
        data = self.socket_.recv(CHUNK_SIZE)
        data = repr(data)[1:-1]
        request = data[0] # the first character is the request
        data = data[1:] # the rest is the data
        print self.peer_.id, '- received', request, data, 'from', self.id

        if request == self.UPDATE:
            self.peer_.files.update(self.id, data)
            self.socket_.sendall(self.peer_.files.serialize())

        if request == self.IDLE:
            if (self.getAction() == self.IDLE):
               time.sleep(.5) # reduce how much we spam the network with useless packets
            self.sendRequest()

        if request == self.CLOSE:
            self.socket_.close()
            self.active = False

    def sendRequest(self):
        action = self.getAction()

        if action == self.UPDATE:
            print self.peer_.id, 'is telling', self.id, 'to update'
            msg = "%s%s" % (self.UPDATE, self.peer_.files.serialize())
            self.socket_.sendall(msg)

            data = self.socket_.recv(CHUNK_SIZE)
            data = repr(data)[1:-1]
            print self.peer_.id, '- received update data', data, 'from', self.id
            self.peer_.files.update(self.id, data)

            self.actions.pop(0)
            self.socket_.sendall(self.IDLE)

        if action == self.IDLE:
            self.socket_.sendall(self.IDLE)

        if self.getAction() == self.CLOSE:
            self.socket_.sendall(self.CLOSE)
            self.socket_.close()
            self.active = False


class Peer():
    def __init__(self, addr, port, peersFile='peers.txt'):
        self.connected = False # becomes true after join() is called
        self.addr = addr
        self.port = port
        self.id = "%s:%d" % (self.addr, self.port)
        self.storage = Storage(port) # Interface to write/read to/from the disk
        self.files = FileStatus(self.storage) # keeps track of what file chunks we have/need
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
                addr, port = peerConnection.split(' ')
                port = int(port)
                self.peers_.append((addr, port))
        except:
            print 'DEBUG:', self.id, '- Error parsing peers file'

    # API method
    def join(self):
        if self.connected:
            return errOK # already connected, no need to join
        if len(self.peers_) == 0:
            return errNoPeersFound

        self.files.addLocalFiles() # add all files that already exist locally in the peer folder

        self.connected = True
        self.listen()
        self.startSync()

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
        for conn in self.peerConnections:
            conn.addAction(Connection.UPDATE)
        return errOK

    # API method
    def query(self, status):
        return errOK

    # API method
    def leave(self):
        self.connected = False

        # stop the syncer thread
        self.syncer.join()

        # stop the listener thread
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((self.addr, self.port)) # connect to self to close to listener thread
        s.close()

        # close all connections to peers
        for conn in self.peerConnections:
            conn.addAction(Connection.CLOSE)
        for conn in self.peerConnections:
            conn.join()

        return errOK

    def listen(self):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.socket.bind((self.addr, self.port))
        self.socket.listen(3)
        self.listener = threading.Thread(target=self.listener)
        self.listener.start()

    def listener(self):
        while self.connected:
            conn, fullAddr = self.socket.accept()
            if not self.connected:
                break
            connection = Connection(self)
            connection.receive(conn)
            connection.start()
            self.peerConnections.append(connection)
        print self.id, '- closing listener thread'
        conn.close()

    def startSync(self):
        self.syncer = threading.Thread(target=self.syncer)
        self.syncer.start()

    def syncer(self):
        while self.connected:
#            print self.id, '- LRC:', self.files.getLeastReplicatedChunk()
            time.sleep(.2)
#            for chunks in self.files:
#                for chunk in chunks:
#
#
#            # wait for all connections to be idle
#            allPeersIdle = False
#            while not allPeersIdle:
#                allPeersIdle = True
#                for conn in self.peerConnections:
#                    if conn.action != Connection.IDLE:
#                        allPeersIdle = False
#                        time.sleep(.1)
#                        break
#
#            # pull the file status from each peer
#            for conn in self.peerConnections:
#                pass
#

    def alreadyHasConnection(self, addr, port):
        for conn in self.peerConnections:
            if conn.addr == addr and conn.port == port:
                return True
        return False


class FileStatus:
    HAVE_ALL_FILES = 0
    NO_FILES = 'n'

    def __init__(self, storage):
        self.files = {} # mapping of file name to array of chunks
        self.storage_ = storage
        self.lock_ = threading.Lock() # prob will need to use this somewhere

    def addLocalFiles(self):
        # TODO get all files in the file system (storage.getLocalFiles) and add them (self.addLocalFile)
        pass

    def addLocalFile(self, fileName):
        self.storage_.writeFile(fileName)
        numChunks = self.storage_.getNumChunks(fileName)
        chunks = [Chunk(Chunk.HAS) for i in range(0, numChunks)]
        self.files[fileName] = chunks
        print 'added local file', self.serialize()

    def addRemoteFile(self, peer, fileName, maxChunks, chunks):
        if fileName in self.files:
            file = self.files[fileName]
        else:
            file = [Chunk() for i in range(0, maxChunks)]
            self.files[fileName] = file
        for peerOwnedChunk in chunks:
            file[peerOwnedChunk].peers.add(peer)
        print 'added remote file from', peer, self.serialize()

    def getLeastReplicatedChunk(self):
        bestFileName = ''
        bestChunk = -1
        leastReplication = sys.maxint
        for fileName in self.files:
            chunks = self.files[fileName]
            for i, chunk in enumerate(chunks):
                if chunk.status == Chunk.NEED:
                    replication = len(chunk.peers)
                    if replication < leastReplication:
                        leastReplication = replication
                        bestFileName = fileName
                        bestChunk = i
                        if replication == 1:
                            return (bestFileName, bestChunk)
        if bestFileName == '':
            return self.HAVE_ALL_FILES
        return (bestFileName, bestChunk)

    def update(self, peer, data):
        if data == self.NO_FILES:
            return
        files = re.split('(?<!\\\)#', data)
        for file in files:
            fileName, chunkInfo = re.split('(?<!\\\);', file)
            chunkInfo = chunkInfo.split(',')
            fileName = self.decode(fileName)
            chunks = [int(i) for i in chunkInfo[1:]]
            maxChunks = int(chunkInfo[0])
            self.addRemoteFile(peer, fileName, maxChunks, chunks)

    # status of what chunks we own: noah.txt;7,1,2,3,5,6#etc.. - "I have chunks 1, 2, 3, 5, 6 of noah.txt which has 7 chunks total"
    def serialize(self):
        text = ''
        first = True
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
            text += "%s;%d%s" % (self.encode(fileName), len(chunks), chunkText)
        if text == '':
            return self.NO_FILES
        return text

    def encode(self, text):
        return text.replace('\\', '\\\\').replace(';', '\\;').replace('#', '\\#')

    def decode(self, text):
        return text.replace('\\#', '#').replace('\\;', ';').replace('\\\\', '\\')

class Storage:
    def __init__(self, port):
        # TODO create a folder called peer<port number>
        pass

    def writeFile(self, fileName):
        # TODO write file locally
        pass

    # TODO hardcoded for now
    def readFile(self, fileName):
        return PEERS_FILE

    # TODO for now I'm just saying each character of the file name is a chunk in the file :)
    def getChunk(self, fileName, chunk):
        return fileName[chunk]

    def getNumChunks(self, fileName):
        return len(fileName)


class Chunk:
    NEED = 'n'
    HAS = 'h'
    GETTING = 'g'

    def __init__(self, status=NEED):
        self.gettingFrom = '' # addr:port of the peer currently transferring this file to us
        self.peers = sets.Set() # set of peers that have this chunk
        self.status = status


class Status:
    def numFiles(self):
        return 0

    def fractionPresentLocally(self, fileNum):
        return -1

    def fractionPresent(self, fileNum):
        return -1

    def minimumReplicationLevel(self, fileNum):
        return -1

    def averageReplicationLevel(self, fileNum):
        return -1


PEERS_FILE = '127.0.0.1 10001\n127.0.0.1 10002'

p1 = Peer('127.0.0.1', 10001)
p2 = Peer('127.0.0.1', 10002)
p1.join()
p2.join()

time.sleep(.5)

p1.insert('noah.txt')

time.sleep(1)

p1.leave()
p2.leave()
