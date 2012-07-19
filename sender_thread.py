##
# Sends requests and data to all other peers
##

from threading import Thread

class SenderThread(Thread):
    def __init__(self):
        Thread.__init__(self)


