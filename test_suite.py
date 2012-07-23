#!/usr/bin/python

import time

from peer import Peer

def test():
    p1 = Peer('localhost', 10001)
    p2 = Peer('localhost', 10002)
    p1.connect()
    p2.connect()
    p1.join('localhost', 10002)
#    p1.write('', [], 0, 0)

    time.sleep(1)

    p1.disconnect()
    p2.disconnect()

    p1.exit()
    p2.exit()

test()
