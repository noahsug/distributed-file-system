#!/usr/bin/python

##
# TO RUN:
# A file named 'peers.txt' needs to be in the same directory as the python source.
# The contents of 'peers.txt' need to be "127.0.0.1 10001\n127.0.0.1 10002\n127.0.0.1 10003"
# Two files, 'file1.txt' and 'file2.txt' need to be present in the home directory and have some content.
##

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

for i in range(20):
    print ' ------------ time', i, '-------------'
    showStatus(p1)
    showStatus(p2)
    showStatus(p3)

    if i == 10:
        p3.leave()

time.sleep(2)
print ' ------------ time', 'end', '-------------'
showStatus(p1)
showStatus(p2)
showStatus(p3)

p1.leave()
p2.leave()
p3.leave()
