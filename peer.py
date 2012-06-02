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
            print "about to connect to", addr, port
            self.socket_.connect((addr, port))
        except:
            print "DEBUG: Cannot connect to peer"
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
        self.peers_ = Peers()
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
            print "listener connected to", addr, conn
            connection = Connection(self)
            connection.receive(conn, fullAddr[0], fullAddr[1])
            connection.start()
            self.peerConnections.append(connection)
            break

    def join(self):
        if self.connected:
            return errOK # already connected, no need to join
        if peers.empty():
            return errNoPeersFound
        connectedPeers = 0
        for peer in self.peers_:
            if peer[0]
            conn = Connection(self)
            conn.connect(peer[0], peer[1])
            conn.start()

    def insert(self, fileName):
        pass

    def query(self, status):
        pass

    def leave(self):
        pass


class Peers:
    peers_ = []

    # TODO should be a filename, not a string
    # TODO peers file shouldn't be specified - it will be peers.txt in base dir
    def __init__(self):
        self.parsePeersFile('localhost 50001')

    def parsePeersFile(self, peersFile):
        if peersFile is '':
            return
        try:
            peerConnections = peersFile.split('\n')
            for peerConnection in peerConnections:
                addr, port = peerConnection.split(' ')
                port = int(port)
                self.peers_.append((addr, port))
                print 'added', addr, port, 'to peers file'
        except:
            print 'DEBUG: Error parsing peers file'

    def __getitem__(self, index):
        return self.peers_[index]


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



p = Peer('localhost', 50001)
