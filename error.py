##
# Provides error codes.
# > 0 means warning, < 0 means error
##

OK             =  0 # Everything good
UnknownWarning =  1 # Unknown warning
FileOutOfDate = 2
UnknownFatal   = -2 # Unknown error
CannotConnect  = -3 # Cannot connect to anything; fatal error
NoPeersFound   = -4 # Cannot find any peer (e.g., no peers in a peer file); fatal
PeerNotFound   =  5 # Cannot find some peer; warning, since others may be connectable
NotActive      = -6 # Can't do said operation because this object is not longer active
CannotReadFile = -7 # Error reading the file
CannotOpenFile = -8
InvalidBufferSize = -9
FileNotFound = -10
FileNotOpen = -11
FileNotOpenForWrite = -12
AlreadyOffline = 13
AlreadyOnline = 14
CannotFullyUpdateFile = 15
InvalidOp = -16
CausedConflict = 17
