#!/usr/bin/python

import time
import dfs_state

data = '1' * (dfs_state.CHUNK_SIZE + 1)
data2 = 'abcdefg' * dfs_state.CHUNK_SIZE

def changeDevice():
    time.sleep(.5)


def testOfflineUsage():
    import mock_network
    from peer import Peer

    p1 = Peer('localhost', 10001)
    p2 = Peer('localhost', 10002)
    p3 = Peer('localhost', 10002)

    p1.open('boobs.txt', 'w')
    p1.write('boobs.txt', data)
    p1.close('boobs.txt')

    p1.markStable('boobs.txt')

    p1.open('boobs.txt', 'w')
    p1.write('boobs.txt', data, len(data))
    p1.write('boobs.txt', data, len(data) * 2)
    p1.close('boobs.txt')

    p1.listFiles()
    p1.goOnline()

    changeDevice()

    p2.goOnline()
    p2.join(p1)
    time.sleep(1)

    p2.listFiles()
    p2.open('boobs.txt', 'w')
    p2.write('boobs.txt', data2, 10)
    p2.close('boobs.txt')
    p2.listFiles()
    p2.goOffline()

    p1.listFiles()

    p1.goOffline()
    p1.delete('boobs.txt')
    p1.delete('boobs.txt.stable')
    p1.exit()

    p2.goOffline()
    p2.delete('boobs.txt')
    p2.delete('boobs.txt.stable')
    p2.exit()

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
