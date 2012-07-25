#!/usr/bin/python

import time

data = '123456789' * 10

def testOfflineUsage():
    import mock_network
    from peer import Peer

    p1 = Peer('localhost', 10001, mock_network.Network())

    p1.open('boobs.txt', 'w')
    p1.write('boobs.txt', data)
    p1.read('boobs.txt', [0]*100)
    p1.close('boobs.txt')

    p1.listFiles([])
    p1.exit()

def testBasicUsage():
    from peer import Peer

    p1 = Peer('localhost', 10001)
    p1.goOnline()

    time.sleep(.2)
    p2 = Peer('localhost', 10002)
    p2.goOnline()

    time.sleep(.1)
    p1.join('localhost', 10002)
#    p1.write('', [], 0, 0)

    time.sleep(.1)
    p1.goOffline()
    p1.exit()

    time.sleep(.1)
    p2.goOffline()
    p2.exit()

    del p1
    del p2

def testLoadingFromState():
    p1 = Peer('localhost', 10001)
    p2 = Peer('localhost', 10002)
    p1.goOnline()
    p2.goOnline()

    time.sleep(1)

    p1.goOffline()
    p2.goOffline()
    p1.exit()
    p2.exit()

def testSerializer():
    import serializer
    from dfs_state import DFS

    bob = (1, 2, 3, 4)
    s = serializer.serialize(bob)
    obj = serializer.deserialize(s)
    print obj

    dfs = DFS()
    s = serializer.serialize(dfs)
    obj = serializer.deserialize(s)
    print obj.id

    nw = {'a': DFS(), 'b': DFS(), 'c': DFS()}
    fs = [1, 2, 3, 4, 5]
    state = (fs, nw)
    s = serializer.serialize(state)
    obj = serializer.deserialize(s)
    print obj


testOfflineUsage()
#testSerializer()
#testBasicUsage()
