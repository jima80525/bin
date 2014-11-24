#!/usr/bin/python
"""
script to modify build.defs files so they are not self-referential.
Turns out that sometimes ant doesn't load them in order.  Grrr.
To be called with
   ./cc.py `find . -name build.defs`
"""
import sys

def fix_propfile(property_file):
    root = dict()

    # read the file and build a dictionary of tokens
    pfile = open(property_file, 'r')
    for line in pfile:
        line = line.strip()
        # don't process comment lines
        if not line.startswith((';', '#')) and len(line):
            key, value = line.split('=')
            key = key.strip()
            value = value.strip()
            root[key] = value
    pfile.close()

    # we have the list of macros present in the file - now reopen the file and
    # read the entire thing in.  We'll do a string.sub on it for each macro.
    # Example:
    pfile = open(property_file, 'r')
    defs = pfile.read()
    pfile.close()

    # replace any macros that are defined in this file with thier definition
    for k,v in root.items():
        defs = defs.replace("${%s}"%k, v)

    # overwrite the file
    pfile = open(property_file, 'w')
    pfile.write(defs)
    pfile.close()

if __name__ == '__main__':
    # skip arg[0]
    for arg in sys.argv[1:]:
        fix_propfile(arg)
        fix_propfile(arg)
