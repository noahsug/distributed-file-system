##
# Represents the version of a file
##

class Version:
    def __init__(self, fileName, numEdits, numChunks, lastEdited):
        self.fileName = fileName
        self.numEdits = numEdits
        self.numChunks = numChunks
        self.lastEdited = lastEdited

    def equals(self, otherVersion):
        return (self.fileName == otherVersion.fileName and self.numEdits == otherVersion.numEdits and self.numChunks == otherVersion.numChunks and self.lastEdited == otherVersion.lastEdited)
    
    def before(self, otherVersion):
        return (self.fileName == otherVersion.fileName and self.numEdits < otherVersion.numEdits)