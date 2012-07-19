##
# Provides a lock.
##

import threading

class Lock:
    def __init__(self, tag):
        self.tag = tag
        self.lock_ = threading.Lock()

    def acquire(self):
        self.lock_.acquire()

    def release(self):
        self.lock_.release()

