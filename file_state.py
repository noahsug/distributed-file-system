##
# Keeps track of the state of each file.
# - Stores which files exist in the DFS.
# - For each file, the # of chunks owned and edit history is stored.
##

from base import Base
from lock import Lock

class FileState(Base):

    def __init__(self, dfs):
        Base.__init__(self, dfs)
        self.lock_ = Lock(dfs)
        self.fileList = {}