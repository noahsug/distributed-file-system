##
# Keeps track of the state of each file.
# - Stores which files exist in the DFS.
# - For each file, the # of chunks owned and edit history is stored.
##

from lock import Lock
from storage import Storage
from file import File
import os.path

class FileState:

    def __init__(self):
        self.lock_ = Lock('FileState')
        self.fileList = []
    
    def addFile(self, filePath):
        if(os.path.isfile(filePath)):
            f = File(os.path.basename(filePath), filePath, Storage.getNumChunks(filePath))
            self.fileList.append(f);

        

            