#!/usr/bin/python

import time

def testBasicUsage():
    from peer import Peer

    p1 = Peer('localhost', 10001)
    p2 = Peer('localhost', 10002)
    p1.connect()
    p2.connect()
#    p1.join('localhost', 10002)
#    p1.write('', [], 0, 0)

    time.sleep(1)

    p1.disconnect()
    p2.disconnect()

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


#testSerializer()
testBasicUsage()
