#!/usr/bin/python

import time
import threading
import socket
import sets

errOK             =  0; # Everything good
errUnknownWarning =  1; # Unknown warning
errUnknownFatal   = -2; # Unknown error
errCannotConnect  = -3; # Cannot connect to anything; fatal error
errNoPeersFound   = -4; # Cannot find any peer (e.g., no peers in a peer file); fatal
errPeerNotFound   =  5; # Cannot find some peer; warning, since others may be connectable

#CHUNK_SIZE = 65536
CHUNK_SIZE = 1 # TODO temporarily making it 1 to make development easier

class Connection(threading.Thread):
    def __init__(self, peer):
        self.peer_ = peer
        threading.Thread.__init__(self)
        self.action = 'idle'

    def connect(self, addr, port):
        self.active = False # false when the connection is closed
        self.addr = addr
        self.port = port
        self.recv_ = False
        self.socket_ = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try :
            self.socket_.connect((addr, port))
            self.active = True
        except:
            print 'DEBUG:', self.peer_.name, '- Cannot connect to peer', addr, port
            return errPeerNotFound
        return errOK

    def receive(self, conn):
        self.active = True
        self.addr = self.port = 0 # we don't know the port or addr until the connection has been made
        self.socket_ = conn
        self.recv_ = True
        return errOK

    def setAction(action):
        self.action = action

    def run(self):
        if self.recv_:
            data = self.socket_.recv(1024)
            data = repr(data)
            addr, port = data[1:-1].split(':')
            port = int(port)

            if self.peer_.alreadyHasConnection(addr, port):
                print self.peer_.name, '- receiver closing duplicate connection'
                self.socket_.sendall('close')
                self.socket_.close()
                self.active = False
            self.socket_.sendall('idle')

        else:
            self.socket_.sendall(self.peer_.addr + ':' + str(self.peer_.port))

        while self.active:
            data = self.socket_.recv(1024)
            data = repr(data)[1:-1]
            print self.peer_.name, '- received', data

            if data == 'idle':
                if self.action == 'idle':
                    time.sleep(.5) # avoid spamming the network with idles

                self.socket_.sendall(self.action)

                if self.action == 'close':
                    self.socket_.close()
                    self.active = False

            if data == 'close':
                print self.peer_.name, '- connector closing connection'
                self.socket_.close()
                self.active = False


class Sync(threading.Thread):
    def __init__(self, peer):
        threading.Thread.__init__(self)
        self.peer_ = peer


class Peer(threading.Thread):
    def __init__(self, addr, port, peersFile='peers.txt'):
        threading.Thread.__init__(self)
        self.name = addr + ':' + str(port)
        self.connected = False # becomes true after join() is called
        self.addr = addr
        self.port = port
        self.storage = Storage(port) # Interface to write/read to/from the disk
        self.status = FileStatus(self.storage) # keeps track of what file chunks we have/need
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
            print 'DEBUG:', self.name, '- Error parsing peers file'

    def join(self):
        if self.connected:
            return errOK # already connected, no need to join
        if len(self.peers_) == 0:
            return errNoPeersFound

        self.status.addLocalFiles() # add all files that already exist locally in the peer folder

        self.connected = True
        self.listen()

        connectedPeers = 0
        failedToConnect = False
        for peer in self.peers_:
            if peer[0] == self.addr and peer[1] == self.port:
                continue

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

    def listen(self):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.bind((self.addr, self.port))
        self.socket.listen(3)
        listener = threading.Thread(target=self.listener)
        listener.start()

    def listener(self):
        while self.connected:
            conn, fullAddr = self.socket.accept()
            if not self.connected:
                break
            connection = Connection(self)
            connection.receive(conn)
            connection.start()
            self.peerConnections.append(connection)
        print self.name, '- closing listener thread'
        conn.close()

    def alreadyHasConnection(self, addr, port):
        for conn in self.peerConnections:
            if conn.addr == addr and conn.port == port:
                return True
        return False

    def insert(self, fileName):
        self.status.addLocalFile(fileName)
        return errOK

    def query(self, status):
        return errOK

    def leave(self):
        self.connected = False
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((self.addr, self.port)) # connect to self to close to listener thread
        s.close()
        for conn in self.peerConnections:
            conn.action = 'close'
        return errOK


class FileStatus:
    files = {} # mapping of name to array of chunks

    def __init__(self, storage):
        self.storage = storage

    def addLocalFiles(self):
        # TODO get all files in the file system (storage.getLocalFiles) and add them (self.addLocalFile)
        pass

    # TODO read from disk and store file under peer folder
    def addLocalFile(self, fileName):
        self.storage.writeFile(fileName)
        numChunks = self.storage.getNumChunks(fileName)
        chunks = [Chunk(Chunk.HAS) for i in range(0, numChunks)] # for now I'm just using the file name and each chunk is one character :)
        self.files[fileName] = chunks
        print 'added local file', self.serialize()

    def addRemoteFile(self, peer, fileName, maxChunks, chunks):
        if fileName in files:
            file = self.files[fileName]
        else:
            file = [Chunk() for i in range(0, maxChunks)]
            self.files[fileName] = file
        for peerOwnedChunk in chunks:
            file[peerOwnedChunk].peers.add(peer)

    def serialize(self):
        text = ''
        for fileName, file in self.files:
            text += fileName + ';' + len(file)


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
    gettingFrom = '' # addr:port of the peer currently transferring this file to us
    peers = sets.Set() # set of peers that have this chunk

    def __init__(self, status=NEED):
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
status1 = p1.join()
status2 = p2.join()

time.sleep(.5)

p1.insert('noah.txt')

time.sleep(.5)

p1.leave()
p2.leave()

print 'p1 join status:', status1
print 'p2 join status:', status2
