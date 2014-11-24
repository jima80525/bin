#!/usr/bin/python
import sys
newlines = list()
f = open("pom.xml", 'r')
for line in f.readlines():
    line = line.rstrip()
    if 'optional' in line:
        line = line.replace('true', 'false')
    if '<version>' in line:
        if '_vB' in line and '-S' in line:
            indx = line.find('_vB')
            line = line[:indx] + "</version>"
        line = line.replace('_', '-')
        line = line.replace('+', '')

    newlines.append(line)
    if 'modelVersion' in line:
        newlines.append("  <name>${module}</name>")

f.close()
f = open("jima.xml", "w")
f.write('\n'.join(newlines))
f.close()

