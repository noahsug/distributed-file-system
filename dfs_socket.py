##
# Custom DFS socket
##
import socket

socket.setdefaulttimeout(2)

class DFSSocket(socket.socket):
    def __init__(self):
        socket.socket.__init__(self, socket.AF_INET, socket.SOCK_STREAM)
        self.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
