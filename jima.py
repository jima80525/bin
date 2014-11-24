#!/usr/bin/python
# JHA must use optparse as omverse still at python 2.6
from mhbuild_classes import *

def fred():
    print "ABOUT TO SCAN JIMA"
    for g in globals():
        if "Build" in g:
            print "testing", g
            print "HERE"
            print
    print "AFTER SCAN"



if __name__ == "__main__":
    sys.exit("no main implemented")
