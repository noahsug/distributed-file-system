##
# Represents the version of a file
##

class Version:
    def __init__(self, fileName, numEdits, numChunks, lastEdited):
        self.fileName = fileName
        self.numEdits = numEdits
        self.numChunks = numChunks
        self.lastEdited = lastEdited
