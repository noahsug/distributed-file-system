#!/usr/bin/python

import threading
import socket

CHUNK_SIZE = 65536
MAX_PEERS = 6
MAX_FILES = 100

class File:
    name_ = ''
    localChunks_ = 0
    totalChunks_ = 0

class Peer:
    def __init__(self, address, port):
        self.address = address
        self.port = port
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.bind((address, port))
        self.socket.listen(1)
        #start accepting connections on listening thread
        
    def listen(self):
        while True:
            conn, addr = self.socket.accept()
            
    def join(self):
        pass
        
    def insert(self, fileName):
        pass
        
    def query(self, status):
        pass
    
    def leave(self):
        pass
    
    def worker(self):
        pass

    #===========================================================================
    # def run(self):
    #    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    #    s.bind(('', 50037))
    #    s.listen(1)
    #    conn, addr = s.accept()
    #    print 'Connected by', addr
    #    while 1:
    #        data = conn.recv(1024)
    #        if not data: break
    #        conn.sendall(data)
    #    conn.close()
    #===========================================================================


class Peers:
    
    def initialize(self, peersFile):
        #peersFile = "128.81.1.4 58293\n129.2.1.4 58273\n121.14.2.1 22741"
        file = peersFile.split('\n')
        for line in file:
            peerInfo = line.split(' ')
            peer = Peer(peerInfo[0], peerInfo[1])


class Status:
    numFiles_ = -1
    fractionPresentLocally_ = -1
    fractionPresent_ = -1
    minimumReplicationLevel_ = -1
    averageReplicationLevel_ = -1
    
    
    

p = Peers()
p.initialize("")
