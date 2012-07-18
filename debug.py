##
# Provides debugging functionality.
##

import lock
import lock import Lock
import peer

class Logger:
    lock_ = Lock('Logger')

    def __init__(self, tag):
        self.tag = tag

    def d(self, msg):
        log('DEBUG', msg)

    def e(self, msg):
        log('ERROR', msg)

    def log(self, verbosity, msg):
        lock_.acquire()
        print '%s # %s %s - %s' % (verbosity, self.tag, peer.id, msg)
        lock_.release()
