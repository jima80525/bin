#!/usr/bin/python
import tarfile
import os
import sys
import commands

# This is a flag which gets set by the -f (for fast!) flag on the command line.
# We generally do a check to remove entries which are directories (which contain
# other files) as some packages have them and some do not.  This is an O(n*n)
# operation which is fine for most package, but mvl contains 17K files and thus
# takes several minutes to run.
skipMVLCheck = False

# This was just some interesting stats we collected while doing the conversion.
# The first is the list of .la files which were in the rpms.
# The second is the list of files containing '/man/'
lasInRpms = list()
manFilesInRpms = list()

# this function is used for both tars and rpms - it removes exceptions from the
# set and also does a full search looking for directory entries.
def removeDirs(setToClean, pkgname):
    tmp = setToClean  # not sure if we need a copy to walk list twice
    toremove = set()
    for f in setToClean:
        ########################################################################
        # this first set of exceptions applies to both rpm and tar file sets.
        ########################################################################
        # glib got pulled into one package instead of five.  I've manually
        # checked that this contains the right info, so skip the errors here.
        # note that the rpm for these libs only contain .la files, so I'm not
        # quite sure what's happening here.
        if 'usr/lib/libgio-2.0' in f or 'usr/lib/libgmodule-2.0' in f or 'usr/lib/libgmodule-2.0' in f or 'usr/lib/libgobject-2.0' in f or 'usr/lib/libgthread-2.0' in f:
            toremove.add(f)
            continue

        # dbus is packaging a .h file as well.  ugh
        if '/usr/lib/dbus-1.0/include/dbus/dbus-arch-deps.h' in f:
            if 'dbus-dev' not in pkgname:
                toremove.add(f)
                continue

        # for some reason these two files were backwards on 8272 - they
        # were in the -dev package not the 'on camera' package where they
        # belong.  We corrected this in the conversion.
        if '/usr/bin/hsl.lua' == f or '/usr/bin/hslsh' == f:
            toremove.add(f)
            continue

        # these are include files that were installed on camera by the imageio
        # rpm.  We removed them from the tar files on camera.
        if '/usr/local/include/omons/imageio/' in f:
            toremove.add(f)
            continue

        # lib omons packages this file in both the dev and 'on camera'
        # rpms.  I've confirmed it is in the dev tarball and we don't
        # want it on camera.
        if '/usr/lib/libomons-check.so' == f:
            toremove.add(f)
            continue

        # omons-settings is including .h files on the camera.  Ugh
        # these were moved to the .dev package
        if '/usr/local/include/omons/settings' in f:
            toremove.add(f)
            continue

        ########################################################################
        # the rest of the checks are only excluding files which are in the
        # rpms and shouldn't be
        ########################################################################
        if '.rpm' in pkgname:
            # filesys has an entry in the rpm file for the root dir.  This is going
            # to be created.
            if '/' == f:
                toremove.add(f)
                continue

            # skip directories that are empty but still in the rpms
            if '/usr/share/ssl/certs' in f or '/usr/share/ssl/private' in f:
                toremove.add(f)
                continue
            # php publishes this as an empty directory
            if 'usr/include/php/include' in f:
                toremove.add(f)
                continue


            # JHA skipping this file - it's only built for x86 by default.
            # The pulse build did some crazy command line options to get it to
            # build.  This is a unit test for ev-compat.  If someone wants it
            # in the new world, they can fix up the build.xml themselves.
            if '/usr/bin/check/check-ev-compat' == f:
                toremove.add(f)
                continue

            # not at all sure how this was building for the pulse build.  I
            # strongly suspect it's not needed on camera (there are several
            # .so files in pam that are not needed) so leaving it out until
            # further notice.
            if '/lib/security/pam_userdb.so' == f:
                toremove.add(f)
                continue

            # iniparse only generated a single rpm on pulse.  It has both .so and
            # .h files.  We split this into two tars in the new system.  These two
            # files are in the ini-parser-dev tarball listed at the top.
            if '/usr/include/dictionary.h' == f or '/usr/include/iniparser.h' == f:
                toremove.add(f)
                continue

            # cerberus was split into a dev package - these are include files
            # that were installed on the camera by the pulse build
            if '/usr/include/omons/fpga/' in f or '/usr/src/kernel/include/linux/omons/fpga/' in f:
                toremove.add(f)
                continue

            # libgpg-error was installing a few lisp files (really) on the nfs
            # filesys.  Pretty sure these are not needed
            if '/usr/share/common-lisp/' in f:
                toremove.add(f)
                continue

            # mvl puts a LOT of documentation on the filesys.  We aren't doing that.
            if '/usr/src/kernel/Documentation/' in f:
                toremove.add(f)
                continue

            # no idea why we're packaging these in the omons rpms
            if '/usr/src/kernel/${build.prefix}/codegen/' in f:
                toremove.add(f)
                continue


            # more mvl flotsam that we don't need
            if '/usr/src/kernel/ivy.xml' == f:
                toremove.add(f)
                continue

            # and even more mvl flotsam that we don't need
            # these appear to be some auto-generated scripts
            if '/usr/src/kernel/scripts/basic/st' in f or \
               '/usr/src/kernel/scripts/genksyms/st' in f or \
               '/usr/src/kernel/scripts/kconfig/st' in f or \
               '/usr/src/kernel/scripts/mod/st' in f or \
               '/usr/src/kernel/scripts/st' in f:
                toremove.add(f)
                continue


            # the 9081 filesys pulse build (at least) was including matterhorn
            # codegen directories.  Pretty sure this is not needed.
            if 'filesys-HEAD' in pkgname and '/codegen/' in f:
                toremove.add(f)
                continue

            # the 9081 ov pulse build is including an ivy.xml file. This should
            # never be installed.
            if 'p-ovanalytics-HEAD' in pkgname and 'ivy.xml' in f:
                toremove.add(f)
                continue

        # this is the code to check for entries that are directories
        # It's not clever code - it simply takes the name, tacks on / and then
        # searches for any other entry that starts with that string.
        isDirname = f + '/'
        for g in tmp:
            if isDirname in g:
                toremove.add(f)

    # finally, remove all those entries we flagged to remove.
    # Yes, this could be done more efficiently.
    for r in toremove:
        setToClean.remove(r)

    return setToClean

# This function pulls out the list of files from an rpm.  It excludes .la files
# and man pages.
def getRpmFilesList(rpmname):
    rpmfiles = set()
    try:
        # eventually I want to expand this to the use the following command:
        #    rpm -qp --queryformat '[%{FILEMODES:perms} %{FILENAMES}\n]'
        # which returns the file permissions.
        lines = commands.getoutput('rpm -q -filesbypkg -p %s'%rpmname).splitlines()
        for l in lines:
            _,_,x = l.rpartition(' ')
            # here's where we pull out the .la and man pages.
            if x.endswith('.la'):
                lasInRpms.append("%s:%s"%(x, rpmname))
            elif '/man/' in x:
                manFilesInRpms.append("%s:%s"%(x, rpmname))
            else:
                rpmfiles.add(x)
    except Exception as e:
        print "failed to process %s" % rpmname, e

    # call the function to remove exceptions.
    rpmfiles = removeDirs(rpmfiles, rpmname)
    return rpmfiles

# This function pulls out the list of files from a tarball.
def getFilesInTar(tarname):
    tarfiles = set()
    try:
        tar = tarfile.open(tarname)
        for item in tar.getnames():
            # construct the full path to match the rpm
            name = '/' + item
            tarfiles.add(name)
        tar.close()
    except Exception as e:
        print "failed to process %s" % tarname, e

    # call the function to remove exceptions.
    tarfiles = removeDirs(tarfiles, tarname)
    return tarfiles

# this builds a list of rpm file names to process (given the directory
# containing those files).  It processes exceptions for packages we are not
# porting to the new system or that have changed.
def getRpmFilenames(rpmdirname):
    rpmFilenames = dict()
    dirList=os.listdir(rpmdirname)
    for fname in dirList:
        if '.rpm' in fname:
            name,_,_ = fname.partition('-HEAD')
            # glib got merged into a single package instead of 5.
            # I have manaully confirmed that these match
            if 'glib-' in name: continue

            # these only contained man pages
            if 'ethtool-pelco-dev' in name: continue
            if 'wide-dhcpv6-dev' == name: continue

            # this only contained la files
            if 'lighttpd-dev' in name: continue

            # intentionally removing libjpeg
            if 'libjpeg' in name: continue

            # these two were merged into the build process, I believe
            if 'customize' in name: continue
            if 'finalize' in name: continue

            # oddly enough, fne-porting has an empty on-camera rpm
            # and only publishes to the dev package
            # use of fname instead of name is intentional
            if 'fne-porting-HEAD' in fname: continue

            # empty dev packages
            if 'p-ovanalytics-dev' in name: continue
            if 'luamd5-dev' in name: continue
            if 'healthmon-dev' == name: continue
            if 'licapp-dev' == name: continue
            if 'mcp-dev' == name: continue
            if 'ntp-dev' == name: continue
            if 'pa-sherlock-dev' == name: continue

            # omons tests was joined into a single package as all of it
            # should only be on the nfs filesys
            if 'omons-tests' in name: continue

            rpmFilenames[name] = fname

    return rpmFilenames

# this builds a list of tar file names to process (given the directory
# containing those files).  It processes exceptions for packages we are not
# porting to the new system or that have changed.
def getTarFilenames(tardirname):
    tarFilenames = dict()
    dirList=os.listdir(tardirname)
    for fname in dirList:
        if '.tgz' in fname:
            # get the name of the package
            name,_,_ = fname.partition('pkg')
            name = name[0:-1].replace('_dev', '-dev')

            # glib got merged into a single package instead of 5.
            # I have manaully confirmed that these match
            if 'glib-dev' == name: continue
            if 'glib_' == name: continue

            # omons tests was joined into a single package as all of it
            # should only be on the nfs filesys
            if 'omons-tests' == name: continue

            # flex is actually included in the old toolchain, but not in the
            # arago toolchain.  It was easier/safer to add for all builds.
            if 'flex' == name or 'flex-dev' == name: continue

            # iniparser was split into normal and dev packages.  pulse was
            # installing the .h files onto the camera
            if 'iniparser-dev' == name: continue

            # cerberus-fox was split into normal and dev packages.  pulse was
            # installing the .h files onto the camera
            if 'cerberus_fox-dev' == name: continue

            # the rest of these are just name changes from pulse to bamboo
            if 'fne' in name: name = name.replace('fne', 'fne-porting')
            if 'core' == name or 'core-dev' == name: name = 'pa-' + name
            if 'alarm' == name or 'alarm-dev' == name: name = 'pa-' + name
            if 'sherlock' in name: name = 'pa-' + name
            if 'userdata' in name: name = 'pa-' + name
            if 'abandonedobject' in name: name = 'pa-plugins-ao';
            if 'directionalmotion' in name: name = 'pa-plugins-dm';
            if 'objectremoval' in name: name = 'pa-plugins-or';
            if 'sceneanalyzer' in name: name = 'pa-plugins-sa';
            if 'stoppedvehicle' in name: name = 'pa-plugins-sv';
            if 'cerberus_fox' == name: name = 'cerberus'
            if 'dhcpv6' == name: name = 'wide-' + name
            if 'ethtool' in name: name = name + '-pelco'
            if 'hsl-dev' in name: name = name + 'el'
            if 'pcp-cy8c27' == name: name = 'pcpcy8c'
            if 'u-boot_bin-' in name : name = 'u-boot'
            if 'u-boot_vars-' in name: name = 'bootvars'
            if 'u-boot_pkg-' in fname: name = 'u-boot-tools'
            # this is a bit trick - note the fname for the final comparison, it
            # is intentional.  Here's the mapping from grant:
            # pkg.tgz -> modules rpm     img.tgz -> mvl rpm     dev-pkg.tgz -> dev rpm
            if 'mvl_dev-' in name:  name = 'mvl-dev'
            if 'mvl_img-' in name:  name = 'mvl'
            if 'mvl_pkg-' in fname: name = 'mvl-modules'

            if 'webui' == name: name = 'p-ovanalytics';
            if 'webui-dev' == name: name = 'p-ovanalytics-dev';
            tarFilenames[name] = fname

    return tarFilenames

def printSortedSet(msg, data):
    print
    print msg
    items = sorted(data, key=lambda item: (int(item.partition(' ')[0]) if item[0].isdigit() else float('inf'), item))
    for item in items: print item

# for a given pair of tar/rpm packages - compare them and print the results
def compareTarVsRpm(tarname, rpmname):
    # here is where we skip MVL when we're not doing a full scan
    if skipMVLCheck and 'mvl' in tarname:
        return False
    if skipMVLCheck and 'mvl' in rpmname:
        return False

    # pull the lists of names from each package
    rpmset = getRpmFilesList(rpmname)
    tarset = getFilesInTar(tarname)

    # python does set algebra!  Yippee!
    tnotr = tarset - rpmset
    rnott = rpmset - tarset

    if tnotr or rnott:
        print
        print "============================================================"
        print "Diff between %s and %s" % (tarname, rpmname)
        print "============================================================"
        if tnotr:
            printSortedSet("in tar not rpm", tnotr)
        if rnott:
            printSortedSet("in rpm not tar", rnott)
        return True
    return False


# allow us to read the -f from the command line to skip mvl processing
from optparse import OptionParser
parser = OptionParser()
parser.add_option("-f", "--fast", dest="fast", help="skip empty directory removal", action="store_true", default=False)
(options, args) = parser.parse_args()
skipMVLCheck = options.fast

# get the directory names from the command line.  Someone clever would have
# figured out which one was the tar dir and which the rpm dir automatically.
# I am not that person.
try:
    tardir = args[0]
    rpmdir = args[1]
except Exception as e:
    exit("failed to specify directories")

# always end with a '/'
if tardir[-1] != '/': tardir = tardir + '/'
if rpmdir[-1] != '/': rpmdir = rpmdir + '/'

# get the list of filenames for both sides, then build sets for the package
# names
rpms = getRpmFilenames(rpmdir)
tars = getTarFilenames(tardir)
tfs = set(tars.keys())
rfs = set(rpms.keys())

# look at that, more set algebra
printSortedSet("packages in tars but not rpms", tfs -rfs)

# even more!j
printSortedSet("packages in rpms but not tars", rfs -tfs)

# intersections, too?!?  this is crazy.
# the intersection should be the list of packages which are in both rpm and tar
# directories
toCheck = rfs.intersection(tfs)

good = list()
numbad = 0

# walk through and compare each of the matching packages
for key in sorted(toCheck):
    if not compareTarVsRpm(tardir + tars[key], rpmdir + rpms[key]):
        good.append(key)
    else:
        numbad = numbad + 1
print

#print "============================================================"
#print "the following .la files were in the rpms"
#print "============================================================"
#for b in lasInRpms:
    #print b
#print
#
#print "============================================================"
#print "the following man files were in the rpms"
#print "============================================================"
#for b in manFilesInRpms:
    #print b
#print

#print "============================================================"
#print "============================================================"
#print "the following modules were ok"
#print "============================================================"
#print "============================================================"
#for g in good:
    #print g
#print

print "num good ", len(good)
print "num bad  ", numbad
