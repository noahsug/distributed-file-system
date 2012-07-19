##
# Keeps track of the state of each file.
# - Stores which files exist in the DFS.
# - For each file, the # of chunks owned and edit history is stored.
##

from lock import Lock

class FileState:
    def __init__(self):
        self.lock_ = Lock('FileState')
