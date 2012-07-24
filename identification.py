class ID:
    def __init__(self, addr='', port=0):
        if addr:
#            self.str = "%s:%d" % (addr, port)
            self.str = str(port - 10000) # TODO for easier debug readibility only
        else:
            self.str = 'id_not_init'

    def __str__(self):
        return self.str
