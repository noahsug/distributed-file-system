##
# Represents the version of a file
##

class Version:
    def __init__(self, fileName, numEdits, numChunks, fileSize, lastEdited):
        self.fileName = fileName
        self.numEdits = numEdits
        self.numChunks = numChunks
        self.lastEdited = lastEdited
        self.fileSize = fileSize

    def equals(self, otherVersion):
        return (self.fileName == otherVersion.fileName and self.numEdits == otherVersion.numEdits and self.numChunks == otherVersion.numChunks and self.fileSize == otherVersion.fileSize and self.lastEdited == otherVersion.lastEdited)
    
    def isOutOfDate(self, otherVersion):
        return (self.fileName == otherVersion.fileName and self.numEdits < otherVersion.numEdits)
    
    def hasLocalChanges(self, otherVersion):
        return (self.fileName == otherVersion.fileName and self.numEdits > otherVersion.numEdits)
        