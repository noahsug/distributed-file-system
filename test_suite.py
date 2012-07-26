#!/usr/bin/python

import time
import dfs_state
import debug

logger = debug.Logger('', dfs_state.DFS(' ', 10000))
def log(msg):
    logger.i(msg)

def changeDevice():
    time.sleep(.5)

def testOfficialUsage():
    # Init
    f11 = 'f11.txt'
    f12 = 'f12.docx'
    f13 = 'f13.pptx'
    f14 = 'f14.txt'
    f21 = 'f21.executable'
    f22 = 'f22.zip'
    f31 = 'f31.jpg'

    fileNames = [f11, f12, f13, f21, f22, f31]
    from peer import Peer
    data = { }
    for file in fileNames:
        f = open('files/' + file, 'r')
        txt = f.read()
        data[file] = [c for c in txt]

    def writeData(d, fileName):
        d.open(fileName, 'w')
        d.write(fileName, data[fileName])
        d.close(fileName)

    dv1 = Peer('localhost', 10001)
    dv1.goOnline()
    dv2 = Peer('localhost', 10002)
    dv2.goOnline()
    dv2.join(dv1)
    dv3 = Peer('localhost', 10003)
    dv3.goOnline()

    writeData(dv1, f11)
    writeData(dv1, f12)
    writeData(dv1, f13)

    writeData(dv2, f21)
    writeData(dv2, f22)

    writeData(dv3, f31)

    log('--------------------- START OF 1 & 2')
    # 1 & 2
    dv1.listFiles()
    dv2.listFiles()
    dv1.markStable(f11)
    dv1.markStable(f12)
    dv1.markStable(f13)
    dv2.markStable(f21)
    dv2.markStable(f22)

    dv1.listFiles()
    dv2.listFiles()

    log('--------------------- START OF 3')
    # 3
    dv2.open(f11, 'r')
    dv2.open(f12, 'r')
    dv2.read(f11, [0]*200)
    dv2.read(f12, [0]*200)
    dv2.close(f11)
    dv2.close(f12)

    dv1.listFiles()
    dv2.listFiles()

    log('--------------------- START OF 4')
    # 4
    dv1.goOffline()
    dv2.open(f11, 'w')
    dv2.write(f11, 'I am device2 and I like to eat cheese')
    dv2.close(f11)
    dv2.open(f12, 'w')
    dv2.write(f12, 'I am device2 and I hate babbies', 10)
    dv2.close(f12)
    dv1.goOnline()

    dv1.listFiles()
    dv2.listFiles()

    log('--------------------- START OF 5')
    # 5
    dv1.pin(f11)
    dv1.goOffline()
    dv2.goOffline()
    dv2.open(f11, 'w')
    dv2.write(f11, ' THIS TEXT IS BEING INSERTED AT OFFSET 400 BY DEVICE 2 ', 400)
    dv2.close(f11)
    dv1.open(f11, 'w')
    dv1.write(f11, ' I REFUSE TO WRITE WHAT DEVICE 2 SAID, BUT I AM STILL INSERTING AT OFFSET 400 ', 400)
    dv1.close(f11)

    dv1.listFiles()
    dv2.listFiles()

    dv1.goOnline()
    dv1.listFiles()
    dv2.listFiles()

    dv2.goOnline()
    dv1.listFiles()
    dv2.listFiles()

    log('--------------------- START OF 6a')
    # 6 a
    dv1.open(f14, 'w')
    dv1.write(f14, 'this file is f14' * 20000)
    dv1.close(f14)

    dv1.listFiles()
    dv2.listFiles()

    log('--------------------- START OF 6b')
    # 6 b
    dv1.delete(f11)

    dv1.listFiles()
    dv2.listFiles()

    log('--------------------- START OF 7')
    # 7
    dv3.join(dv1)
    dv3.listFiles()

    log('--------------------- START OF 8')
    # 8
    dv3.pin(f12 + '.stable')
    dv3.listFiles()

    log('--------------------- START OF 9')
    # 9




    dv1.open(f11 + '.p1', 'r')
    dv1.read(f11 + '.p1')
    dv1.close(f11 + '.p1')


    log('--------------------- END')

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
