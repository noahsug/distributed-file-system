class ID:
    def __init__(self, port, addr):
        self.port = port
        self.addr = addr
        self.str = "%s:%d" % (self.addr, self.port)
