##
# Provides debugging functionality.
##

import threading
from threading import Thread

logLock_ = threading.Lock()
def log(self, msg):
    logLock_.acquire()
    print msg
    logLock_.release()
