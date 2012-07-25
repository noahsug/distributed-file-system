##
# A mock network for testing purposes
##

import error as err

class Network:
    def loadFromState(self, peers):
        pass

    def connect(self):
        pass

    def connectTo(self, dfs):
        pass

    def disconnect(self):
        pass

    def getFile(self, fileName):
        return -1

    def fileEdited(self):
        pass

    def getState(self):
        return []

