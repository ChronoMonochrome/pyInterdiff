import sys
from pyinterdiff import *

file1, file2 = sys.argv[1:3]
readFile = lambda x: open(x).readlines()
diff1, diff2 = parseDiff(readFile(file1)), parseDiff(readFile(file2))

print compareDiffs(diff1, diff2)

