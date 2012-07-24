from file_system import FileSystem
from dfs_state import DFS
import array

dfs_ = DFS('192.168.0.2', 10000)
fs = FileSystem(dfs_)

strz = 'abcd'
t = buffer(strz)

fs.add('file1.txt', 1)

# test list function
li = fs.list()
for f in li:
    print f.fileName + '(IsDeleted = ' + str(f.isDeleted) + ')'
    f.state = "r"

buf = []
fs.readIntoBuffer('file1.txt', buf, 0, 1)

stri = buf
print stri

print "Can Read:" + str(fs.canRead('file1.txt'))
print "Can Write:" + str(fs.canWrite('file1.txt'))

fs.write('file1.txt', strz, 8, 4)


print('done')