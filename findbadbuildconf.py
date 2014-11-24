#!/usr/bin/python
import sys
import os
import fnmatch

def convertComponents(base_directory):
    pattern = 'buildconf.py'

    for root, dirs, files in os.walk (base_directory):
        for _ in fnmatch.filter(files, pattern):
            filetoread = os.path.join(root, 'buildconf.py')
            with open(filetoread) as f:
                for line in f:
                    if 'maxwell_8280' in line or \
                       'maxwell_9280' in line or \
                       'ambarella_amb_s2' in line or \
                       'PC_x86' in line:
                        print root, line.rstrip()





convertComponents(os.getcwd())
