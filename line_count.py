#!/usr/bin/env python3
import sys

lines = list()
with open(sys.argv[1]) as f:
    for linenum, line in enumerate(f):
        # print(linenum, len(line))
        lines.append((len(line)-1, linenum+1))

for tup in sorted(lines):
    print(tup)
# print("here i am")
# print(sys.argv[0], sys.argv[1])
