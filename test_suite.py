#!/usr/bin/python

from dfs_state import DFS
from debug import Logger

def test():
    log = Logger('TestSuite', DFS(0, 0))
    log.d('hey thar')
    log.e('cow boy')
    log.w('OH NO')

test()
