#!/usr/bin/python
import os, sys, glob, tarfile, shutil, stat

def untar(args):
    tar_dirs = list()
    for tarname in args:

        tar = tarfile.open(tarname)
        tar.extractall('.')
        tar.close()
        # JHA fixup a bug in bugreport which is producing /var/calib/color with
        # bad permissions
        os.chmod('bugreport/var/calib/color', stat.S_IRWXU)


        # part the ipconfig.txt file to get the ip address and rename the dir
        # to that.  If it's not found, just name the dir to whatever the tarball
        # is.
        new_name = None
        with open('bugreport/ifconfig.txt', 'r') as f:
            prefix_length = len('inet addr:')
            for line in f.readlines():
                if 'inet addr:' in line:
                    # this is a tad ugly.  lstrip pulls off leading spaces,
                    # [] removes the 'inet addr:' prefix
                    # split(' ') splits the remainer on space
                    # and [0] takes the first value from the split
                    new_name = line.lstrip()[prefix_length:].split(' ')[0]
                    break

        basename, _ = os.path.splitext(tarname)
        if not new_name:
            new_name = "%sbugreport" % basename

        # store this name in our list
        tar_dirs.append(new_name)
        # make sure it's not already there before we repopulate it
        shutil.rmtree(new_name, True)
        print "Untarred %s to %s" % (basename, new_name)
        os.rename('bugreport', new_name)
        os.rename(tarname, "%s.tgz" % new_name)
    return tar_dirs

def build_raw_logs(dir):
    outfile_name = "%s.log" % dir
    with open(outfile_name, 'w') as outfile:
        for logname in sorted( \
                              glob.glob(os.path.join(dir, 'var/log',
                                                     'system.log*')),
                              reverse=True):
            with open(logname) as infile:
                for line in infile:
                    outfile.write(line)

def testline_reset(line):
    line = line.rstrip()
    if 'RESETTYPE' in line:
        print line

_LINE_TESTS = [ testline_reset, ]

def test_log_file(infile_name):
    print "processing %s" %infile_name
    with open(infile_name) as infile:
        for line in infile:
            for test in _LINE_TESTS:
                test(line)

def generate_versions_file(dirs):
    versions = dict()
    for dir in dirs:
        filename = os.path.join(dir, 'etc', 'version')
        print filename
        with open(filename, 'r') as version_file:
            version = version_file.read()
            versions[dir] = version.rstrip()

# if specific tarballs are on command line, use those, else just use *.tgz
if len(sys.argv) > 1:
    args = sys.argv[1:]
else:
    args = glob.glob('*.tgz')

dirs = untar(args)
for d in dirs:
    build_raw_logs(d)
    test_log_file("%s.log"%d)

generate_versions_file(dirs)

