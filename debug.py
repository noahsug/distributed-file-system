##
# Provides debugging functionality.
##

from lock import Lock
from system_state import dfs

class Logger:
    lock_ = Lock('Logger')

    def __init__(self, tag):
        self.tag = tag

    def d(self, msg):
        self.log('DEBUG', msg)

    def w(self, msg):
        self.log('WARN ', msg)

    def e(self, msg):
        self.log('ERROR', msg)

    def log(self, verbosity, msg):
        Logger.lock_.acquire()
        print '%s> %s # %s: %s' % (dfs.id, verbosity, self.tag, msg)
        Logger.lock_.release()
