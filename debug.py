##
# Provides debugging functionality.
##

import threading

class Logger:
    lock_ = threading.Lock()
    verbosity = ['VERBO', 'DEBUG', 'WARN ', 'ERROR']

    def __init__(self, tag, dfs):
        self.tag_ = tag
        self.dfs_ = dfs

    def v(self, msg):
        self.log('VERBO', msg)

    def d(self, msg):
        self.log('DEBUG', msg)

    def w(self, msg):
        self.log('WARN ', msg)

    def e(self, msg):
        self.log('ERROR', msg)

    def log(self, verbosity, msg):
        if not verbosity in Logger.verbosity:
            return
        Logger.lock_.acquire()
        shorthand = self.dfs_.port - 10000
        print '%s> %s # %s: %s' % (shorthand, verbosity, self.tag_, msg)
        Logger.lock_.release()
