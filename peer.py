#!/usr/bin/python

import threading
import socket

CHUNK_SIZE = 65536
MAX_PEERS = 6
MAX_FILES = 100


class Peer(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)

    def run(self):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.bind(('', 50037))
        s.listen(1)
        conn, addr = s.accept()
        print 'Connected by', addr
        while 1:
            data = conn.recv(1024)
            if not data: break
            print 'Server received', repr(data)
            conn.sendall(data)
            conn.close()


class Peers(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)

    def run(self):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect(('localhost', 50037))
        s.sendall('Hello, world')
        data = s.recv(1024)
        s.close()
        print 'Received', repr(data)


class Status:
    numFiles = -1
    fractionPresentLocally = -1
    fractionPresent = -1
    minimumReplicationLevel = -1
    averageReplicationLevel = -1

peer = Peer()
peer.start()

peers = Peers()
peers.start()
