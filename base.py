##
# A base class for all DFS classes
##

from debug import Logger

class Base:
    def __init__(self, dfs):
        self.dfs_ = dfs
        self.log_ = Logger(self.__class__.__name__, self.dfs_)

