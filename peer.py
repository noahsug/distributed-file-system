#!/usr/bin/python

import threading
import socket

CHUNK_SIZE = 65536
MAX_PEERS = 6
MAX_FILES = 100


class Peer:
    def __init__(self, address, port):
        self.address = address
        self.port = port
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.bind((address, port))
        s.listen(1)
        #start accepting connections on listening thread
        
    def listen(self):
        while True:
            conn, addr = s.accept()
            

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
        peersFile = "128.81.1.4 58293\n129.2.1.4 58273\n121.14.2.1 22741"
        file = peersFile.split("\n")
        for line in file:
            peerInfo = line.split(" ")
            peer = Peer(peerInfo[0], peerInfo[1])


class Status:
    numFiles = -1
    fractionPresentLocally = -1
    fractionPresent = -1
    minimumReplicationLevel = -1
    averageReplicationLevel = -1

p = Peers()
p.initialize("")
