#!/usr/bin/python

import time

from dfs_state import DFS
from peer import Peer

def test():
    p1 = Peer('localhost', 10001)
    p2 = Peer('localhost', 10002)

    time.sleep(1)

    p1.disconnect()
    p2.disconnect()

test()
