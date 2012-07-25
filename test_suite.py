#!/usr/bin/python

import time
import dfs_state
import debug

log = debug.Logger('', dfs_state.DFS(' ', 10000))

def changeDevice():
    time.sleep(.5)

def testOfficialUsage():
    # Init
    from peer import Peer
    data = {
        'f11.txt': None,
        'f12.docx': None,
        'f13.pptx': None,
        'f21.executable': None,
        'f22.zip': None,
        'f31.jpg': None
        }

    for file in data:
        f = open('files/' + file, 'r')
        txt = f.read()
        data[file] = [c for c in txt]

    dv1 = Peer('localhost', 10001)
    dv1.goOnline()
    dv2 = Peer('localhost', 10002)
    dv2.goOnline()
    dv3 = Peer('localhost', 10003)
    dv3.goOnline()
    dv2.join(dv1)
    dv3.join(dv1)

    def writeData(d, fileName):
        d.open(fileName, 'w')
        d.write(fileName, data[fileName])
        d.close(fileName)

    writeData(dv1, 'f11.txt')
    writeData(dv1, 'f12.docx')
    writeData(dv1, 'f13.pptx')

    writeData(dv2, 'f21.executable')
    writeData(dv2, 'f22.zip')

    writeData(dv3, 'f31.jpg')

    # 1
    dv1.listFiles()
    dv2.listFiles()
    dv1.markStable('f11.txt')
    dv2.markStable('f21.executable')

    # 2
    dv1.listFiles()
    dv2.listFiles()

    # 3
    dv2.open('f11.txt', 'r')
    dv2.open('f12.docx', 'r')
    dv2.read('f11.txt', [0]*200)
    dv2.read('f12.docx', [0]*200)
    dv2.close('f11.txt')
    dv2.close('f12.docx')

    dv1.exit()
    dv2.exit()
    dv3.exit()


def testTwoPeerUsage():
    from peer import Peer
    data = ['1', '2', '3'] * dfs_state.CHUNK_SIZE
    data2 = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i'] * dfs_state.CHUNK_SIZE

    p1 = Peer('localhost', 10001)
    p2 = Peer('localhost', 10002)

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
    p2.listFiles()
    p2.open('boobs.txt', 'w')
    p2.write('boobs.txt', data2, 10)
    p2.close('boobs.txt')
    p2.listFiles()
    p2.goOffline()

    p1.unpin('boobs.txt')

    p1.listFiles()
    p1.open('boobs.txt', 'r')
    p1.read('boobs.txt', [0]*100)
    p1.goOffline()
    p1.delete('boobs.txt')
    p1.delete('boobs.txt.stable')
    p1.exit()

    p2.goOffline()
    p2.delete('boobs.txt')
    p2.delete('boobs.txt.stable')
    p2.exit()

    log.i('Tests Done!')

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


testOfficialUsage()
#testTwoPeerUsage()
#testSerializer()
#testBasicUsage()
