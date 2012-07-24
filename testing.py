from file_system import FileSystem
from dfs_state import DFS

dfs_ = DFS('192.168.0.2', 10000)
fs = FileSystem(dfs_)

fs.add('file1.txt', 1)

# test list function
li = fs.list()
for f in li:
    print f.fileName + '(IsDeleted = ' + str(f.isDeleted) + ')'
    f.state = "r"

buf = [' '] * 4
fs.readIntoBuffer('file1.txt', buf, 0, 4)
print buf

buf[0] = 'z'

print "Can Read:" + str(fs.canRead('file1.txt'))
print "Can Write:" + str(fs.canWrite('file1.txt'))

fs.write('file1.txt', buf, 6, 4)
fs.writeChunk('file1.txt', 0, 'databack')
fs.write('file1.txt', buf, 12, 4)

print fs.isUpToDate('file1.txt')

print "numedits = " + str(fs.logical_.fileList_['file1.txt'].latestVersion.numEdits)

#fs.delete('file1.txt')
#fs.deleteLocalCopy('file1.txt')

li = fs.list()
for f in li:
    print f.fileName + '(IsDeleted = ' + str(f.isDeleted) + ')'
    f.state = "r"

print('done')