#!/usr/bin/python
"""
omdepends.py
------------
This script builds a tree of interdependent components using a
content-hash-based method for caching intermediate build results.  From any
starting component, the script walks the list of its dependent components and
does one of three things (in order):

1) copy the build artifacts from a local cache

2) copy the build artifacts from a remote cache TO the local cache and then do
   step 1

3) build the component and publish it to the local (and possibly remote cache)
   and then do step 1

Once the dependencies are resolved, the script produces a manifest file for the
given component based on the SHA of the files in the component directory (more
on this later), the SHA of the tools, and the SHA of each of the dependent
components' manifests.  This manifest is stored with the build artifact in the
caches AND it is run through the SHA1 algorithm to produce the key by which this
version of this artifact will be stored.

Having the SHA for the given component, we can check to see if an exact copy of
this has already been built and simply use that if it has.  If it has not, then
we must call each of the build commands for the component and publish the
resulting artifacts.

This is a recursive function which builds or resolves the dependencies in a
depth-first fashion.  It can be run from any component in the system and only
the subtree on which it depends will be checked (and possibly built).

Some features of this algorithm for our purposes:
* Artifacts are stored independent of which branch they are in.  This means that
  builds that are identical are reused for everyone when possible.

* Doing a "full clean build" is simply a matter of using command line options to
  disable the cache lookups.

* Fully erasing the local (and remote!) cache will have no adverse effect on the
  builds other than the first rounds of builds will take longer

* Creating a new branch which has only trivial changes from an already-built
  branch will build quickly, either locally or on the server.

* All top-level builds are self-contained.  Because the artifact lookup process
  is indexed off of the actual content of the component and its dependents, any
  artifact pulled will match what would have been built with the code that is
  present in the given commit tree.  This is in contrast to our ivy-based build
  system which will use whatever the most-recently built version of a given
  component is, even if it does not match what is in the commit tree.

* Because of the self-contained nature of the builds described above, we can
  have the build servers only do full product builds instead of having build
  jobs for each component.

* Also because of the self-contained builds, the bisect feature of git will
  actually be useful for solving bugs.

* Each component is built by its own rules.  There is no need to cram all
  components into an Ant build system.  This should allow us to get rid of the
  goofy ant files in external-3rdparty component and also allow us to start
  transitioning to new build tools (cmake, anyone?) on a component-by-component
  basis.


Component Configuration
-----------------------

For each component in the system there is a configuration file (called
buildconf.py) which contains four items:

1) the name of the component

2) a list of build commands to build the component

3) a list of configurations this component is built for

4) a list of components upon which this component depends


Each of these items are written as a python assignment statement giving a string
value (or list of string values) for the item.

The name of the component is a simple string such as "deimos" or
"matterhorn-api".

The list of build commands is a sequence of bash shell commands which are
executed in order to produce the build product in the .publish directory of the
component.  The number and complexity of this list is limited by bash and the
memory on your machine.   There currently is not a way to do token substitution
into the command lines.

The list of configurations contains all of the configuration outputs produced by
this component.  Examples are [ 'dm81xx', 'x86' ] and [ 'maxwell_8280',
'maxwell_9280' ].  These are used when determining which artifacts to pull from
dependencies.

The list of dependencies is a list of components.  Each component here is
specified by its path relative to the root of the repo in which you are working.
An examples are 'omons/deimos' or 'external-3rdparty/zlib/1.2.3'.

How is the sha for a given set of files generated?
--------------------------------------------------

To start, we need to be clear that the SHA in question is the sha we use to
represent the contents of the files in the given component's directory tree.
This is NOT the SHA of the component's manifest file, which is used for storing
and retrieving artifacts.

There are two methods used to generate the component's sha.  The first and most
obvious one is to use the sha that Git computed when it committed the directory
tree.  This is what we use if the 'git status -z -u all .' command indicates
that no files have been modified from HEAD.  If, on the other hand, there are
modified files, then each file listed in the git status output has its contents
run through the SHA1 algorithm.  The result of all files going through this
filter produces the SHA for the component.

This should produce false-positives, but not false-negatives.  In other words,
there are conditions which will cause this algorithm to rebuild a component when
none of the files the build cares about have changed.  It should not be possible
to make a change to any file in the component's directory tree and not have a
build triggered with the following caveat: we are using git status to determine
which files have changed, so files covered by a .gitignore directive will not
been seen by this algorithm.  This is intentional.

Theory of Operation
-------------------
There are two main structures in the script: a BuildFile which represents a
component and a Cache which handles all interactions with both local and remote
caches.

The BuildFile class is recursive, creating BuildFiles for each dependent
component in its cstor.  There is a global list of already created BuildFiles to
restrict us to only creating one structure for each component.  The BuildFile
recurs before it attempts to create its manifest, thus insuring that all of its
dependencies are present in the local cache (we'll see how in a bit).  After
creating each dependency, all the given component needs to store is the name and
sha of that component.

Once it has all of these, it can then proceed to create its manifest, sha1 it,
and then determine if it needs to be rebuilt or not. Rebuilding will results in
the build artifacts being published to the local and remote cache.   Searching
the cache starts with the local cache and, if that misses, proceeds to the
remote cache.  A remote cache hit results in the artifacts being copied to the
local cache from whence they are used.

Building the components is simply a matter of executing each of the lines given
in the configuration file.  This allows a great deal of flexibility in how each
component is built.  (And greatly sped up the testing of this tool!).  The
requirements for build script are:

1) artifacts are generated in the .publish directory of the component

2) it cleans up all other generated files.

Artifacts are currently stored locally to a build_output directory in the
current user's home directory (usually root in the omverse:
/opt/omtools/omverse/root/build_output).  The remote cache is stored in on
fcbuildmaster and should be readily seen through a web browser. (INSERT PATH
HERE)

"""
# JHA must use optparse as omverse still at python 2.6
from optparse import OptionParser
import socket # for gethostname
import logging, sys, os, fnmatch, hashlib, shutil, time, traceback
from git import *
from subprocess import call

scriptVersionNumber="0.5.0"

# Get the version info for the Tools and cache this so we only have to construct
# that object once.
gToolsVersion = None
def GetToolsVersion():
    global gToolsVersion
    if gToolsVersion == None:
        toolsRepo = Repo("/opt/omtools/")
        gToolsVersion = (u"omtools version: ", toolsRepo.head.commit.hexsha)
    return gToolsVersion

# This is a file-local cache of BuildFile objects.  It allows us to recur the
# dependency tree and not re-compute the hash
gBuildFileCache = dict()

# This is the global cache object which abstracts the local and remote caches
gCache = None

# This holds command line options
gOptions = None

def FlushAndCall(cmd):
    ''' Utility to flush output streams before doing system call '''
    sys.stdout.flush()
    sys.stderr.flush()
    logging.debug("CMD: %s"%cmd)
    return call(cmd, shell=True)

class BuildFile:
    """Encapsulate a single omons component"""

    def __init__(self, path, CodeRepo):
        ''' Build an object representing the component specified in the path
        parameter.  '''

        # start by checking cache and populating it if we're not already there
        if path in gBuildFileCache:
            raise Exception("Tried to create exising build file:"+path)
        gBuildFileCache[path] = self

        # read the buildconf.py file for this module
        self.mModuleName, buildCmd, configs, deps = self.ReadBuildConfFile(path)

        self.mHashSHA1 = None
        self.mCodeRepo = CodeRepo
        self.mModulePath = path
        self.elapsed = 0

        # convert dep list into a list of dicts so we can associate hash with
        # name
        self.mDependencies = list()

        #print "[BUILD] \t%30s\t%s"%(self.mModuleName, self.mHashSHA1)
        #self.BuildAndPublish(buildCmd, configs)
        #return
    #def dummy(self):
        for dep in deps:
            fullPath = os.path.join(self.mCodeRepo._working_tree_dir, dep)
            if fullPath in gBuildFileCache:
                depFile = gBuildFileCache[fullPath]
            else:
                depFile = BuildFile(fullPath, CodeRepo)

            # save the name, hash pairing for computing our manifest note that
            # the name is actually the full path to the module
            self.mDependencies.append(depFile)

        #now we have the dep tree filled out - get the hash for this component
        self.GetHash()

        # and, if this hash doesn't exist in the cache, build it!
        if not gCache.Search(os.path.join(self.mModuleName, self.mHashSHA1)):
            if sys.stdout.isatty():
                print "[\033[91mBUILD\033[0m] \t%30s\t%s"%(self.mModuleName, self.mHashSHA1)
            else:
                print "[BUILD] \t%30s\t%s"%(self.mModuleName, self.mHashSHA1)
            if not gOptions.dryrun:
                self.BuildAndPublish(buildCmd, configs)
        else:
            if sys.stdout.isatty():
                print "[\033[92mCACHE\033[0m] \t%30s\t%s"%(self.mModuleName, self.mHashSHA1)
            else:
                print "[CACHE] \t%30s\t%s"%(self.mModuleName, self.mHashSHA1)

    def ReadBuildConfFile(self, path):
        ''' read the buildconf.py file for this module '''
        buildinfo = {}
        filetoread = os.path.join(path, "buildconf.py")
        execfile(filetoread, dict(), buildinfo) # second param is ignored by us
        logging.debug("%s:Conf read:%s"%(path, buildinfo))
        return buildinfo['name'], buildinfo['buildCmd'], buildinfo['configs'], buildinfo['deps'],

    def GetHash(self):
        # if we already have a valid hash, just return it
        if self.mHashSHA1:
            return (self.mHashSHA1)

        hashLines = []

        # get the common header info
        sepStr = "+".ljust(79,"-")+"+\n"
        hashLines.append(sepStr)
        hashLines.append(self.FormatLine((u"Omons Build Script -- Version: %s"%scriptVersionNumber).center(77)))
        hashLines.append(sepStr)
        # JHA TODO should cache tools version and pass it in
        hashLines.append(self.FormatLineWithSha(GetToolsVersion()))
        hashLines.append(sepStr)
        hashLines.append(self.FormatLine(u"Component:"))
        hashLines.append(self.FormatLineWithSha(self.GetCodeVersion()))
        hashLines.append(sepStr)
        hashLines.append(self.FormatLine(u"Dependencies:"))
        # now recurse the dependencies to get the hash value
        for entry in self.mDependencies:
            hashLines.append(self.FormatLineWithSha((entry.mModuleName, entry.GetHash())))
        hashLines.append(sepStr)

        self.mManifest = ''.join(hashLines)
        self.mHashSHA1 = hashlib.sha1(self.mManifest).hexdigest()
        return self.mHashSHA1

    def GetSHA1ForModule(self, repo, currentDirectory):
        """ Use the git status command here to see the state of the current
        directory.  the -z option returns a stable (across git versions)
        condensed form of the status command.  The "-u all" option tells git to
        report on all untracked files (as well as the usual suspects).  If there
        is nothing changed in the component, status will return nothing and
        we'll ask git for the sha of the tree of this component.

        If something has changed, the sha of the component will be the sha of
        the contents of ALL files that have changed.  This is consevative in
        that it will produce false-positives and we'll try to build components
        in which non-building files have changed.  The expectation is that the
        build will run quickly in this case as nothing has changed that the
        build cares about.
        """
        baseDirectory = repo._working_tree_dir

        # run the status command with "-z -u all"
        stat = repo.git.status(currentDirectory, z=True, u='all')
        if not len(stat):
            # Nothing changed - use the git sha
            relPath = os.path.relpath(currentDirectory, baseDirectory)
            tree = repo.head.commit.tree
            commitSha = tree[relPath].hexsha
            logging.debug("Sha pulled from GIT for %s: %s"%(currentDirectory, commitSha))
        else:
            # something changed on the local filesys.  Go through and compute the
            # hash of all the contents of all the files that have changed.  Note
            # that this will not track adding empty directories (who cares).
            logging.debug("output of git status: %s"%stat)
            hasher = hashlib.sha1()
            for line in stat.split('\0'):
                if line: # z format returns an empty line at end
                    _,filename = line.split()
                    fullFileName = os.path.join(baseDirectory, filename)
                    # only get the hash for actual files
                    if os.path.isfile(fullFileName):
                        with open(fullFileName) as f:
                            hasher.update(f.read())

            commitSha = hasher.hexdigest()
            logging.debug("Sha pulled from files for %s: %s"%(currentDirectory, commitSha))
        return commitSha

    def GetCodeVersion(self):
        return (u""+self.mModuleName, self.GetSHA1ForModule(self.mCodeRepo, self.mModulePath))

    def FormatLine(self, line):
        return "| "+line.ljust(77)+"|\n"

    def FormatLineWithSha(self, data):
        return "| "+data[0].ljust(36)+data[1]+" |\n"

    def CreateComponentDir(self, subdir):
        """Creates the subdir for the given component and returns the full path
           to that subdir.
        """
        fullpath = os.path.join(self.mModulePath,subdir)
        if not os.path.isdir(fullpath):
            os.makedirs(fullpath)
        return fullpath

    def BuildAndPublish(self, cmds, configs):
        # setup the local directory for building
        publishDir = self.CreateComponentDir('.publish')
        cacheDestDir = self.CreateComponentDir('.ivy')

        # pull the deps from cache - they should all be present
        for depFile in self.mDependencies:
            gCache.CopyFromCache(os.path.join(depFile.mModuleName, depFile.mHashSHA1), cacheDestDir, configs)

        # build this component
        time1 = time.time()
        os.chdir(self.mModulePath)
        for cmd in cmds:
            if FlushAndCall(cmd) != 0:
                errorMsg = "%s failed to build on this command: %s"%(self.mModuleName, cmd)
                raise  RuntimeError(errorMsg)
        time2 = time.time()
        self.elapsed = time2 - time1
        logging.info('%s function took %0.3f s' % (self.mModuleName, (time2-time1)*1.0))

        # write the manifest file
        with open(os.path.join(publishDir,self.mModuleName+".txt"),"w") as f:
            f.write(self.mManifest)

        # at this point we should have the necessary artifacts in the
        # current directory -- push them to the allowed cache
        # remote overrides local
        gCache.Publish(publishDir, os.path.join(self.mModuleName, self.mHashSHA1))

class Cache:
    def __init__(self, search=True, remotePublish=False):
        self.mAllowLocalSearch   = search
        self.mAllowRemoteSearch  = search
        self.mAllowLocalPublish  = True # JHA for now always allow local publish
        self.mAllowRemotePublish = remotePublish
        self.server = "builder@fcbuildmaster.pelco.org"
        self.serverPath = "/var/www/html/artifacts/omons/"
        self.mLocalCachePath = os.path.join(os.path.expanduser("~"),"build_cache/omons/")

    def PerformSSHCommand(self, hostname, command):
        return FlushAndCall("/usr/bin/ssh %s \"%s\""%(hostname, command))

    def PerformSCPCommand(self, srcPath, dstPath):
        return FlushAndCall("/usr/bin/scp -q %s %s"%(srcPath, dstPath))

    def Search(self, dstDir):
        dstRemoteDir = os.path.join(self.serverPath, dstDir)
        target = os.path.join(self.mLocalCachePath, dstDir)

        if self.mAllowLocalSearch:
            if os.path.isdir(target):
                return True

        if self.mAllowRemoteSearch:
            # now check for the existence of the files
            if self.PerformSSHCommand(self.server,"stat "+dstRemoteDir+" >& /dev/null") == 0:
                # the directory exists. Copy it to local cache
                if not os.path.isdir(target):
                    os.makedirs(target)

                self.PerformSCPCommand(self.server+":"+dstRemoteDir+"/*", target);
                return True

        return False

    def CopyFromCache(self, dstDir, cacheDestDir, Configurations):
        """ Copy the files into the destination directory """

        confLookUps = {
            'dm81xx'           : [ 'dm81xx', 'pelco_maxwell' ],
            'x86'              : [ 'x86' ],
            'ambs2'            : [ 'ambs2' ],
            'maxwell_8280'     : [ 'maxwell_8280', 'dm81xx', 'pelco_maxwell' ],
            'maxwell_9280'     : [ 'maxwell_9280', 'dm81xx', 'pelco_maxwell' ],
            'ambarella_amb_s2' : [ 'ambarella_amb_s2', 'dm81xx', 'pelco_maxwell' ],
            'bigsur'           : [ 'bigsur', 'ambs2' ],
            'PC_x86'           : [ 'PC_x86', 'x86' ],
            'pelco_maxwell'    : [ 'pelco_maxwell' ],
        }

        target = os.path.join(self.mLocalCachePath, dstDir)

        for entry in Configurations:
            # Make the output dir if needed
            ConfDir = os.path.join(cacheDestDir, entry)
            if not os.path.isdir(ConfDir):
                os.makedirs(ConfDir)

            # JHA TODO FIX THIS
            # rats.  Need to special case omons-lsp as maps to dm81xx.
            # This tells it to copy the maxwell_8280 target to the dm81xx
            # directory
            if 'omons-lsp' in target:
                entry = 'maxwell_8280'

            # now scan the list and copy files to the dest
            for (root, dirs, files) in os.walk(target):
                for name in files:
                    for confName in confLookUps[entry]:
                        if confName in name or name.endswith('.txt'):
                            logging.debug("copying %s to %s"%(os.path.join(root, name), ConfDir))
                            shutil.copy(os.path.join(root, name), ConfDir)

    def PublishBuildTimes(self, times):
        # copy files to local cache
        target = os.path.join(self.mLocalCachePath, "buildtimes")
        shutil.rmtree(target, True) # remove pre-existing cache for this sha
        shutil.copytree(srcDir, target)

    def Publish(self, srcDir, dstDir):
        if self.mAllowRemotePublish:
            # copy files up to remote server
            remoteDir = os.path.join(self.serverPath, dstDir)
            self.PerformSSHCommand(self.server,"mkdir -p "+ remoteDir)
            self.PerformSCPCommand(srcDir + "/*", self.server+":"+remoteDir)

        if self.mAllowLocalPublish:
            # copy files to local cache
            target = os.path.join(self.mLocalCachePath, dstDir)
            shutil.rmtree(target, True) # remove pre-existing cache for this sha
            shutil.copytree(srcDir, target)

def main():
    # parse command line
    parser = OptionParser()
    parser.add_option("-v", "--verbose", dest="verbose", help="turn on verbose output", action="store_true", default=False)
    parser.add_option("-d", "--dryrun", dest="dryrun", help="only report what would be built", action="store_true", default=False)
    parser.add_option("-r", "--enable-remote-publish", dest="remotePublish", help="published generated artifacts to the remote server", action="store_true", default=False)
    parser.add_option("-n", "--no-cache-search", dest="cacheSearch", help="disable cache - force full build", action="store_false", default=True)
    #local and remote search and publish
    global gOptions
    (gOptions, args) = parser.parse_args()
    if gOptions.verbose == True:
        logging.basicConfig(level=logging.DEBUG,
                            format='%(asctime)s %(levelname)s %(message)s')

    print "Omons new build tool"
    print "===================="
    currentDirectory= os.getcwd()
    mGitRepo = Repo(currentDirectory)

    global gCache
    gCache = Cache(gOptions.cacheSearch, gOptions.remotePublish)

    # need to recurse down the tree and pull in the dependencies (or build them if we are allowed)
    temp = BuildFile(currentDirectory, mGitRepo)
    print "Processed %d components"%len(gBuildFileCache)

if __name__ == "__main__":

    #name = socket.gethostname()
    #print name
    #exit()
    scriptStart = time.time()
    try:
        main()
    except Exception as e:
        print e
        print "BUILD FAILED"
        traceback.print_exc()
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(exc_type, fname, exc_tb.tb_lineno)
    scriptEnd = time.time()

    print "%30s\t%s"%('module','build time')
    for v in gBuildFileCache.values():
        if v.elapsed != 0:
            print "%30s\t%s"%(v.mModuleName, v.elapsed)
    print('Entire run took %0.3f s' % ((scriptEnd-scriptStart)*1.0))

