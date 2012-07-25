##
# Provides debugging functionality.
##

import threading

console = open('.output.log', 'w')

class Logger:
    lock_ = threading.Lock()
    lastPeer = ''
    verb = ['V', '!!!D', 'W!!', 'E!!!!', '']
    used = [0, 1, 2, 3, 4]

    def __init__(self, tag, dfs):
        self.tag_ = tag
        self.dfs_ = dfs

    def v(self, msg):
        self.log(0, msg)

    def d(self, msg):
        self.log(1, msg)

    def w(self, msg):
        self.log(2, msg)

    def e(self, msg):
        self.log(3, msg)

    def i(self, msg):
        self.log(4, msg)

    def log(self, verbosity, msg):
        if not verbosity in Logger.used:
            return
        Logger.lock_.acquire()
        v = Logger.verb[verbosity]
        if not v:
            id = '    '
            if Logger.lastPeer != str(self.dfs_.id):
                Logger.lastPeer = str(self.dfs_.id)
                id = '%s> ' % self.dfs_.id
            msg = '%s%s' % (id, msg)
            print msg

        msg = '%s> %s # %s: %s' % (str(self.dfs_.id), v, self.tag_, msg)
        console.write(msg + '\n')
        Logger.lock_.release()
