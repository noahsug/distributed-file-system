##
# Keeps track of the state of the system and handles serialization.
# This includes global information, such as the addr and port of the peer.
##

from identification import ID

class dfs:
    id = ID()
    addr = 0
    port = 0
