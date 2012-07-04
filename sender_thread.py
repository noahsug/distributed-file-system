import threading
from threading import Thread

class SenderThread(Thread):
    def __init__(self):
        Thread.__init__(self)

    def sayHi(self):
        print 'hi thar'

