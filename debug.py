##
# Provides debugging functionality.
##

import threading

class Logger:
    lock_ = threading.Lock()
    verbosity = ['V', 'D', 'W', 'E']

    def __init__(self, tag, dfs):
        self.tag_ = tag
        self.dfs_ = dfs

    def v(self, msg):
        self.log('V', msg)

    def d(self, msg):
        self.log('D', msg)

    def w(self, msg):
        self.log('W', msg)

    def e(self, msg):
        self.log('E', msg)

    def log(self, verbosity, msg):
        if not verbosity in Logger.verbosity:
            return
        Logger.lock_.acquire()
        print '%s> %s # %s: %s' % (str(self.dfs_.id), verbosity, self.tag_, msg)
        Logger.lock_.release()
