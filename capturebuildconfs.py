#!/usr/bin/python
import sys
import os
import fnmatch
import shutil

class OmbuildPlatformBuild():
    def __init__(self, options, path, cache, top_level, context):
        pass
OmbuildProductBuild = OmbuildPlatformBuild
AssemblyBuild = OmbuildPlatformBuild
NoopBuild = OmbuildPlatformBuild
CmakeBuild = OmbuildPlatformBuild
# JHA this next one is an error
ProductBuild = OmbuildPlatformBuild

def convertComponents(base_directory):
    pattern = 'buildconf.py'

    savedir = os.path.join(base_directory, "confs")
    print savedir
    for root, dirs, files in os.walk (base_directory):
        for _ in fnmatch.filter(files, pattern):
            print root
            buildinfo = {}
            confFileName = os.path.join(root, "buildconf.py")
            execfile(confFileName, globals(), buildinfo) # second param is ignored by us
            bld = buildinfo['ComponentBuild'](None, None, None, None, globals())
            print bld
            print bld.name
            newfile = os.path.join(savedir, bld.name + '.py')
            print newfile
            shutil.copyfile(confFileName, newfile)

convertComponents(os.getcwd())


