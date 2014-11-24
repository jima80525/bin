#!/usr/bin/python
import tarfile

import os
path=".ivy"
unique = {}

def testTarAgainstUnique(tarname):
    try:
        if 'phoenix_pkg_' in tarname:
            return
        tar = tarfile.open("%s/%s" % (path, tarname))
        #itemnames = tar.getnames()
        for item in tar.getmembers():
            itemname = item.name
            #print itemname
            #tar.getisdir()
            if not item.isdir() and itemname in unique and 'lib/modules/2' not in itemname:
                if 'phoenix_pkg_' not in tarname or 'phoenix_pkg_' not in unique[itemname]:
                    print "Found a dup: %s was in %s and %s" % (itemname, tarname, unique[itemname])
            unique[itemname] = tarname
        tar.close()
    except Exception as e:
        print "failed to process %s" % tarname, e




dirList=os.listdir(path)
for tarname in dirList:
    if '.tgz' in tarname:
        #print tarname
        testTarAgainstUnique(tarname)

#print unique
