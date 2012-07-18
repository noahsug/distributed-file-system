##
# Each listening thread is pairs with one peer. It listens for data and
# requests and updates the sending thread with new work to do.
##

import threading
from threading import Thread

class ListenerThread(Thread):
    def __init__(self):
        Thread.__init__(self)


