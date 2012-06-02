#!/usr/bin/python

import time
import threading
import socket

errOK             =  0; # Everything good
errUnknownWarning =  1; # Unknown warning
errUnknownFatal   = -2; # Unknown error
errCannotConnect  = -3; # Cannot connect to anything; fatal error
errNoPeersFound   = -4; # Cannot find any peer (e.g., no peers in a peer file); fatal
errPeerNotFound   =  5; # Cannot find some peer; warning, since others may be connectable

CHUNK_SIZE = 65536
MAX_PEERS = 6
MAX_FILES = 100

class Connection(threading.Thread):
    def __init__(self, peer):
        self.peer_ = peer
        threading.Thread.__init__(self)

    def connect(self, addr, port):
        self.addr = addr
        self.port = port
        self.recv_ = False
        self.socket_ = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try :
            self.socket_.connect((addr, port))
        except:
            print "DEBUG: Cannot connect to peer", addr, port
            return errPeerNotFound
        return errOK

    def receive(self, conn, addr, port):
        self.addr = addr
        self.port = port
        self.socket_ = conn
        self.recv_ = True
        return errOK

    def run(self):
        print "connection complete to", self.addr, self.port
        self.socket_.close()


class Sync(threading.Thread):
    def __init__(self, peer):
        threading.Thread.__init__(self)
        self.peer_ = peer


class Peer(threading.Thread):
    def __init__(self, addr, port):
        threading.Thread.__init__(self)
        self.connected = False
        self.addr = addr
        self.port = port
        self.peerConnections = []
        self.peers_ = []
        self.parsePeersFile()
        self.listen()

    def listen(self):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.bind((self.addr, self.port))
        self.socket.listen(3)
        listener = threading.Thread(target=self.listener)
        listener.start()

    def listener(self):
        while True:
            conn, fullAddr = self.socket.accept()
            print "listener connected to", fullAddr
            connection = Connection(self)
            connection.receive(conn, fullAddr[0], fullAddr[1])
            connection.start()
            self.peerConnections.append(connection)
            break

    # TODO should be a filename, not a string
    # TODO peers file shouldn't be specified - it will be peers.txt in base dir
    def parsePeersFile(self):
        peersFile = PEERS_FILE
        if peersFile == '':
            return
        try:
            line = peersFile.split('\n')
            for peerConnection in line:
                addr, port = peerConnection.split(' ')
                port = int(port)
                self.peers_.append((addr, port))
                print 'added', addr, port, 'from peers file'
        except:
            print 'DEBUG: Error parsing peers file'

    def join(self):
        if self.connected:
            return errOK # already connected, no need to join
        if len(self.peers_) == 0:
            return errNoPeersFound

        connectedPeers = 0
        failedToConnect = False
        for peer in self.peers_:
            if peer[0] == self.addr and peer[1] == self.port:
                print "skipping adding self - ", peer
                continue
            conn = Connection(self)
            status = conn.connect(peer[0], peer[1])
            if status == errPeerNotFound:
                failedToConnect = True
            else:
                conn.start()
                connectedPeers += 1

        if connectedPeers == 0:
            return errNoPeersFound
        if failedToConnect:
            return errPeerNotFound
        return errOK

    def insert(self, fileName):
        pass

    def query(self, status):
        pass

    def leave(self):
        pass


class File:
    name_ = ''
    localChunks_ = 0
    totalChunks_ = 0


class Status:
    numFiles_ = -1
    fractionPresentLocally_ = -1
    fractionPresent_ = -1
    minimumReplicationLevel_ = -1
    averageReplicationLevel_ = -1


PEERS_FILE = 'localhost 50001\nlocalhost 50002'

p1 = Peer('localhost', 50001)
p2 = Peer('localhost', 50002)
time.sleep(.1)
status = p1.join()
time.sleep(.1)
print 'p1 join status:', status
