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
        self.addr = self.port = 0
        self.socket_ = conn
        self.recv_ = True
        return errOK

    def setAction(action):
        self.action = action

    def run(self):
        if self.recv_:
            data = self.socket_.recv(1024)
            data = repr(data)
            addr, port = data[1:-1].split(':') # 'addr port' into (addr, port)
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
    def __init__(self, addr, port):
        threading.Thread.__init__(self)
        self.name = addr + ':' + str(port)
        self.connected = False # becomes true after join() is called
        self.addr = addr
        self.port = port
        self.peerConnections = [] # the list of sockets for each peer
        self.peers_ = [] # the list of peers to connect to when join is called
        self.parsePeersFile()

    # TODO peersFile should be a filename, not a string that we parse
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
                #print 'added', addr, port, 'from peers file'
        except:
            print 'DEBUG:', self.name, '- Error parsing peers file'

    def join(self):
        if self.connected:
            return errOK # already connected, no need to join
        if len(self.peers_) == 0:
            return errNoPeersFound

        self.connected = True
        self.listen()

        connectedPeers = 0
        failedToConnect = False
        for peer in self.peers_:
            if peer[0] == self.addr and peer[1] == self.port:
                #print 'skipping adding self - ', peer
                continue

            conn = Connection(self)
            status = conn.connect(peer[0], peer[1])
            if status == errPeerNotFound:
                #print 'failed to connect to', peer
                failedToConnect = True
            else:
                conn.start()
                self.peerConnections.append(conn)
                connectedPeers += 1
                #print 'connected to', peer

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
    files = []


class File:
    name = ''
    localChunks = []
    totalChunks = 0
    status = 'need'


class Status:
    numFiles_ = -1
    fractionPresentLocally_ = -1
    fractionPresent_ = -1
    minimumReplicationLevel_ = -1
    averageReplicationLevel_ = -1


PEERS_FILE = '127.0.0.1 10001\n127.0.0.1 10002'

p1 = Peer('127.0.0.1', 10001)
p2 = Peer('127.0.0.1', 10002)
status1 = p1.join()
status2 = p2.join()

time.sleep(1)

p1.leave()
p2.leave()

print 'p1 join status:', status1
print 'p2 join status:', status2
