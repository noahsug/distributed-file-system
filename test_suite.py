#!/usr/bin/python

from dfs_state import DFS
from debug import Logger
from peer import Peer

def test():
    log = Logger('TestSuite', DFS(0, 0))
    log.d('Test starting')

    p = Peer(0, 0)
    p.connect()
    p.disconnect()

test()
