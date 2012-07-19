#!/usr/bin/python

from debug import Logger

def test():
    log = Logger('TestSuite')
    log.d('hey thar')
    log.e('cow boy')
    log.w('OH NO')

test()
