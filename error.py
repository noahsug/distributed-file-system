##
# Provides error codes.
##

OK             =  0 # Everything good
UnknownWarning =  1 # Unknown warning
UnknownFatal   = -2 # Unknown error
CannotConnect  = -3 # Cannot connect to anything; fatal error
NoPeersFound   = -4 # Cannot find any peer (e.g., no peers in a peer file); fatal
PeerNotFound   =  5 # Cannot find some peer; warning, since others may be connectable
NotActive      = -6 # Can't do said operation because this object is not longer active
CannotReadFile = -7 # Error reading the file
InvalidBufferSize = -8
FileNotFound = -9
