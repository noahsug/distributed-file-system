class ID:
    def __init__(self, port=0, addr=0):
        if port:
            self.str = "%s:%d" % (self.addr, self.port)
        else:
            self.str = 'id not init'

    def init(self, port, addr):
        self.str = "%s:%d" % (self.addr, self.port)

    def __str__(self):
        return self.str
