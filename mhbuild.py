#!/usr/bin/python
""" This is the main modules for building components.  See notes in other
modules for details, esp on how dependencies are generated.
"""
# JHA must use optparse as omverse still at python 2.6
import optparse
import logging, sys, os
import mhbuild_classes
import mhcache

def parse_command_line(args):
    """ Gets options and board parameter. """
    #usage = "usage: %prog [options] board"
    #parser = optparse.OptionParser(usage=usage)
    parser = optparse.OptionParser()
    parser.add_option("", "--build_number", dest="build_number",
                      help="sequence number of this build", action="store",
                      type="int")
    parser.add_option("", "--release_version", dest="release_version",
                      help="release version of build", action="store",
                      type="string", default="DAILY")
    parser.add_option("-n", "--buildfs_only", dest="buildfs_only",
                      help="only create buildfs, no tftp, sdcard or PPMs",
                      action="store_true", default=False)
    parser.add_option("-b", "--board", dest="board",
                      help="board rev (i.e. A0)",
                      # JHA TODO how to allow component to default?
                      action="store_true", default='A0')
    parser.add_option("-p", "--publish", dest="publish",
                      help="publish results to servers", action="store_true",
                      default=False)
    parser.add_option("-v", "--verbose", dest="verbose",
                      help="turn on verbose output", action="store_true",
                      default=False)
    parser.add_option("-d", "--dryrun", dest="dryrun",
                      help="only report what would be built",
                      action="store_true", default=False)
    parser.add_option("", "--enable-remote-publish", dest="remotePublish",
                      help="published generated artifacts to the remote server",
                      action="store_true", default=False)
    parser.add_option("", "--no-cache-search", dest="cacheSearch",
                      help="disable cache - force full build",
                      action="store_false", default=True)

    (options, args) = parser.parse_args()
    if options.verbose == True:
        logging.basicConfig(level=logging.DEBUG,
                            format='%(asctime)s %(levelname)s %(message)s')
    else:
        logging.basicConfig(format='%(asctime)s %(levelname)s %(message)s')

    # publish implies not buildfs_only
    if options.publish:
        options.buildfs_only = False

    return (options, args)

#rm -rf config
#   ['/home/jima/work/omons/external-3rdparty/luamd5/1.1.2']
#rm -rf simd/jsimdcfg.inc
#   ['/home/jima/work/omons/external-3rdparty/libjpeg-turbo/1.1.90']
#rm -rf config.h.in
#   ['/home/jima/work/omons/external-3rdparty/libjpeg-turbo/1.1.90']
#rm -rf Makefile.in
#   ['/home/jima/work/omons/external-3rdparty/libjpeg-turbo/1.1.90']
#rm -rf config.h.in~
#   ['/home/jima/work/omons/external-3rdparty/libjpeg-turbo/1.1.90']
#rm -f build.defs
#   ['/home/jima/work/omons/products/8280']
#rm -rf aclocal.m4
#   ['/home/jima/work/omons/external-3rdparty/libjpeg-turbo/1.1.90']
#rm -f aclocal.m4
#   ['/home/jima/work/omons/external-3rdparty/libxml2/2.9.0']
#rm -rf install-sh
#   ['/home/jima/work/omons/external-3rdparty/libjpeg-turbo/1.1.90']
#rm -rf depcomp
#   ['/home/jima/work/omons/external-3rdparty/libjpeg-turbo/1.1.90']
#rm -f Make.Rules
#   ['/home/jima/work/omons/external-3rdparty/libcap/2.20']
#rm -rf .scratch
#   ['/home/jima/work/omons/products/8280']
#rm -rf config.sub
#   ['/home/jima/work/omons/external-3rdparty/libjpeg-turbo/1.1.90']
#rm -rf missing
#   ['/home/jima/work/omons/external-3rdparty/libjpeg-turbo/1.1.90']
#rm -f	config.h.in~
#   ['/home/jima/work/omons/external-3rdparty/rsyslog/5.9.5']
#rm -rf config.guess
#   ['/home/jima/work/omons/external-3rdparty/libjpeg-turbo/1.1.90']
#rm -rf java/Makefile.in
#   ['/home/jima/work/omons/external-3rdparty/libjpeg-turbo/1.1.90']
#rm -rf .depends
#   ['/home/jima/work/omons/external-3rdparty/boost/1.51.0']
#rm -rf ltmain.sh
#   ['/home/jima/work/omons/external-3rdparty/libjpeg-turbo/1.1.90']
#rm -rf configure
#   ['/home/jima/work/omons/external-3rdparty/libjpeg-turbo/1.1.90']
#rm -f Makefile config.log config.status
#   ['/home/jima/work/omons/external-3rdparty/wide-dhcpv6/20080615']
#rm -rf aplay/arecord
#   ['/home/jima/work/omons/external-3rdparty/alsa-utils/1.0.25']
#rm -rf simd/Makefile.in
#   ['/home/jima/work/omons/external-3rdparty/libjpeg-turbo/1.1.90']


def main(args):
    """ Main routine for running build command. """
    (options, args) = parse_command_line(args)
    start_path = os.getcwd()

    cache = mhcache.Cache(options.cacheSearch, options.remotePublish)

    print "FIRST TIME"
    bld = mhbuild_classes.read_build_conf_file(options, start_path, cache, True)

    for arg in args:
        try:
            getattr(bld, arg.lower())(arg.lower())
        except AttributeError as error:
            print error
            sys.exit("FAILED:Unknown command: %s" %arg)

if __name__ == "__main__":
    main(sys.argv)
