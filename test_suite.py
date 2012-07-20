#!/usr/bin/python

import time

from dfs_state import DFS
from debug import Logger
from peer import Peer

def test():
    log = Logger('TestSuite', DFS(0, 0))
    log.v('Test starting')

    p = Peer('localhost', 0)
    p.connect()
    p.disconnect()

test()
