class ID:
    def __init__(self, addr='', port=0):
        if addr:
            self.str = "%s:%d" % (addr, port)
        else:
            self.str = 'id_not_init'

    def __str__(self):
        return self.str
