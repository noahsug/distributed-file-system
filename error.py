##
# Provides error codes.
##

OK             =  0; # Everything good
UnknownWarning =  1; # Unknown warning
UnknownFatal   = -2; # Unknown error
CannotConnect  = -3; # Cannot connect to anything; fatal error
NoPeersFound   = -4; # Cannot find any peer (e.g., no peers in a peer file); fatal
PeerNotFound   =  5; # Cannot find some peer; warning, since others may be connectable
