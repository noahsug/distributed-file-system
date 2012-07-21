##
# Provides a lock.
##

import threading
import dfs_state

from base import Base

class Lock(Base):
    def __init__(self, dfs=dfs_state.NullDFS, tag=''):
        Base.__init__(self, dfs)
        self.lock_ = threading.Lock()
        self.tag_ = tag

    def acquire(self):
        self.lock_.acquire()

    def release(self):
        self.lock_.release()
