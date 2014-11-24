#!/usr/bin/python
import sys
import os
import fnmatch

def convertComponents(base_directory):
    pattern = 'buildconf.py'

    confs = dict()
    rms = dict()
    ombuilds = dict()
    for root, dirs, files in os.walk (base_directory):
        for _ in fnmatch.filter(files, pattern):
            filetoread = os.path.join(root, 'buildconf.py')
            filetowrite = os.path.join(root, 'buildconf.py')
            convert_build_conf_file(filetoread, filetowrite)

def convert_build_conf_file(filetoread, filetowrite):
    ''' read the buildconf.py file for this module '''
    buildinfo = {}
    #filetoread = os.path.join(path, "buildconf.py")
    execfile(filetoread, dict(), buildinfo) # second param is ignored by us

    if 'maxwell_8280' in buildinfo['configs'] or \
       'maxwell_9280' in buildinfo['configs'] or \
       'ambarella_amb_s2' in buildinfo['configs'] or \
       'PC_x86' in buildinfo['configs']:
        parent = 'ProductBuild'
    else:
        parent = 'PlatformBuild'
    with open(filetowrite, 'w') as newfile:
        newfile.write( "class ComponentBuild  ( %s ):\n" % parent)
        newfile.write( "    name = '%s'\n" % (buildinfo['name']))
        newfile.write( "    configs = [ '%s',  ]\n"% ('\', \''.join(buildinfo['configs'])))
        newfile.write( "    deps = [\n")
        for d in buildinfo['deps']:
            newfile.write( "        '%s',\n"% d)
        newfile.write( "    ]\n")


convertComponents(os.getcwd())
