#!/usr/bin/python

import time
import peer
from peer import *

def showStatus(p):
    p.query(status)
    txt = ''
    for i in range(status.numFiles()):
        txt += '\t %d - (%f, %f, %f, %f)' % (i, status.fractionPresentLocally(i), status.fractionPresent(i), status.minimumReplicationLevel(i), status.averageReplicationLevel(i))
    print "%s: %s" % (p.id, txt)

status = Status()
p1 = Peer('127.0.0.1', 10001)
p2 = Peer('127.0.0.1', 10002)
p3 = Peer('127.0.0.1', 10003)

print p1.join()
print p2.join()
print p3.join()

p2.insert('~/file1.txt')
p3.insert('~/file2.txt')

for i in range(14):
    print ' ------------ time', i, '-------------'
    showStatus(p1)
    showStatus(p2)
    showStatus(p3)

#    if i == 19:
#        p3.leave()

time.sleep(2)
print ' ------------ time', '22', '-------------'
showStatus(p1)
showStatus(p2)
showStatus(p3)

p1.leave()
p2.leave()
p3.leave()
