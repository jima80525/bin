#!/usr/bin/python
""" Defiles classes used by buildconf component modules and loads buildconf from
the component.
"""
import logging, sys, os, time
from git import *
from mhutils import *

# This is a file-local cache of BuildFile objects.  It allows us to recur the
# dependency tree and not re-compute the hash
G_COMPONENT_BUILD_CACHE = dict()

class GeneralBuild():
    """ Root of component builds.  Should be subclassed for platform and product
    specific builds. """
    publish_ombuild_cmd = None
    def __init__(self, options, path, cache, top_level):
        ''' Build an object representing the component specified in the path
        parameter.  '''
        # start by checking cache and populating it if we're not already there
        if path in G_COMPONENT_BUILD_CACHE:
            raise Exception("Tried to create exising build file:"+path)
        G_COMPONENT_BUILD_CACHE[path] = self

        # store away command line options
        self.options = options
        self.top_level = top_level
        self.cache = cache

        # set defaults - these should be overridden in buildconf files
        #self.name = None
        #self.configs = None
        #self.deps = None

        # most of these command just call reombuild with the cmd
        self.configure = self.general_command
        self.build = self.general_command
        self.static_analysis = self.general_command
        self.install = self.general_command
        self.clean = self.general_command

        # these are used for depends command
        self.sha = None
        self.path = path
        self.elapsed = 0
        self.manifest = None
        self.dependencies = None

    def publish(self, _):
        ''' Publish and depends are almost the same operation.  Depends recurs
        building or loading each of this component's deps as needed.  It does
        not build the top level as it's expected you called it in order to
        manually build at the top.  Publish does the same except it builds at
        the top level and publishes that to the cache.
        '''
        self.top_level = False
        self.depends(None)

    def depends(self, _):
        """ Checks the dependency tree and either builds or loads from cache.
        """
        # convert dep list into a list of BuildFiles so we can associate hash
        # with name
        self.dependencies = list()
        for dep in self.deps:
            full_path = os.path.join(get_code_repo()._working_tree_dir, dep)
            if full_path in G_COMPONENT_BUILD_CACHE:
                dep_file = G_COMPONENT_BUILD_CACHE[full_path]
            else:
                dep_file = read_build_conf_file(self.options, full_path,
                                               self.cache, False)
                getattr(dep_file, 'depends')('depends')

            # save the name, hash pairing for computing our manifest note that
            # the name is actually the full path to the module
            self.dependencies.append(dep_file)

        #now we have the dep tree filled out - get the hash for this component
        myhash = self.get_hash()

        # and, if this hash doesn't exist in the cache, build it!
        if not self.top_level:
            if not self.cache.search(os.path.join(self.name, myhash)):
                if sys.stdout.isatty():
                    print "[\033[91mBUILD\033[0m] \t%30s\t%s" % (self.name,
                                                               myhash)
                else:
                    print "[BUILD] \t%30s\t%s" % (self.name, myhash)
                if not self.options.dryrun:
                    self.build_to_cache()
            else:
                if sys.stdout.isatty():
                    print "[\033[92mCACHE\033[0m] \t%30s\t%s" % (self.name,
                                                               myhash)
                else:
                    print "[CACHE] \t%30s\t%s" % (self.name, myhash)
        else:
            # this is the case when we're doing a 'build depends' in a component
            self.depends_to_devroot()

    def build_to_cache(self):
        ''' Build the component and put the artifact into the cache. '''
        # setup the local directory for building
        publish_dir = create_component_dir(self.path, '.publish')
        cache_dest_dir = create_component_dir(self.path, '.ivy')

        # pull the deps from cache - they should all be present
        for dep_file in self.dependencies:
            self.cache.copy_from_cache(os.path.join(dep_file.name,
                                                    dep_file.sha),
                                 cache_dest_dir, self.configs)

        # build this component by calling publish
        time1 = time.time()
        os.chdir(self.path)
        self._ombuild_publish('depends') # pylint: disable=E1101
        time2 = time.time()
        self.elapsed = time2 - time1
        logging.info('%s function took %0.3f s' , self.name, (time2-time1)*1.0)

        # write the manifest file
        with open(os.path.join(publish_dir, self.name+".txt"), "w") as man_file:
            man_file.write(self.manifest)

        # at this point we should have the necessary artifacts in the
        # current directory -- push them to the allowed cache
        # remote overrides local
        self.cache.publish(publish_dir, os.path.join(self.name, self.sha))

    def depends_to_devroot(self):
        ''' Build the artifact in place. '''
        cache_dest_dir = create_component_dir(self.path, '.ivy')
        print "deps to devroot", cache_dest_dir

        # pull the deps from cache - they should all be present
        for dep_file in self.dependencies:
            self.cache.copy_from_cache(os.path.join(dep_file.name,
                                                    dep_file.sha),
                                 cache_dest_dir, self.configs)

    def get_hash(self):
        '''Returns the sha of this component as it appears on disc.  Constructs
        the hash if necessary. '''

        # if we already have a valid hash, just return it
        if self.sha:
            return (self.sha)

        hash_lines = []

        # get the common header info
        separator_str = "+".ljust(79,"-")+"+\n"
        hash_lines.append(separator_str)
        hash_lines.append(self.format_line((u"Omons Build Script -- " \
                                           "Version: %s" % \
                                           get_script_version()).center(77)))
        hash_lines.append(separator_str)
        # JHA TODO should cache tools version and pass it in
        hash_lines.append(self.format_line_with_sha(get_tools_version()))
        hash_lines.append(separator_str)
        hash_lines.append(self.format_line(u"Component:"))
        hash_lines.append(self.format_line_with_sha(self.get_code_version()))
        hash_lines.append(separator_str)
        hash_lines.append(self.format_line(u"Dependencies:"))
        # now recurse the dependencies to get the hash value
        for entry in self.dependencies:
            hash_lines.append(self.format_line_with_sha((entry.name,
                                                     entry.get_hash())))
        hash_lines.append(separator_str)

        self.manifest = ''.join(hash_lines)
        self.sha = hashlib.sha1(self.manifest).hexdigest()
        return self.sha

    def get_code_version(self):
        ''' Helper function to format string. '''
        return (u""+self.name, get_sha_for_module(self.path))

    def format_line(self, line):
        ''' Helper function to format string. '''
        return "| "+line.ljust(77)+"|\n"

    def format_line_with_sha(self, data):
        ''' Helper function to format string. '''
        return "| "+data[0].ljust(36)+data[1]+" |\n"

    def general_command(self, cmd):
        ''' Most of the ombuild command (i.e. build, install, static-analysis)
        generalize into this function. '''
        print "%s" % (cmd.upper())
        shcmd = "/opt/omtools/bin/reombuild  %s" % (cmd)
        logging.debug("CMD: %s", shcmd)
        if shell_cmd(shcmd) != 0:
            print
            sys.exit("BUILD FAILED: %s failed to build on this command: %s" % \
                     (self.name, cmd))

    def distclean(self, cmd):
        ''' Want to have some non-ombuild clean up for this as many components
        leave flotsam on the harddrive which messes up our git dependency
        checking. '''
        self.general_command(cmd)
        self.extra_cleanup(cmd)

    def extra_cleanup(self, cmd):
        ''' Does the extra clean up required to facilitate our git/sha based
        dependency checking to work. '''
        general_cleanup_entries = [
            '__Build*',
            'autom4te.cache',
            '.ivy',
            'devroot',
            'results',
            '.build_out',
        ]
        shcmd = "rm -rf %s" % (' '.join(general_cleanup_entries))
        if shell_cmd(shcmd) != 0:
            print
            sys.exit("BUILD FAILED: %s failed to build on this command: %s" % \
                     (self.name, cmd))
        # component-specific special-cleanup files here
        try:
            self.special_cleanup()
        except:
            # just ignore errors here - it might not exist
            pass

    def _ombuild_publish(self, cmd):
        print "_ombuild_PUBLISH"
        shcmd = "touch devroot;/opt/omtools/bin/reombuild  -f publish.xml " \
                "-Dbuild.skip.ivy=true -Dbuild.in.depends=true " \
                "-Dbuild.configurations=%s %s" % \
                (','.join(self.configs), self.publish_ombuild_cmd)
        if shell_cmd(shcmd) != 0:
            sys.exit("%s failed to build on this command: %s"%(self.name, cmd))

        # add extra clean up commands just to help out with the git-sha
        # consistency
        self.extra_cleanup(cmd)


class PlatformBuild( GeneralBuild ):
    ''' Sub class for building components which are not product-specific. The
    only difference is in the publish command - use the build-all version.
    '''
    publish_ombuild_cmd = 'build-all'

class ProductBuild( GeneralBuild ):
    ''' Sub class for building components which ARE product-specific. The only
    difference is in the publish command - use the build-all-platforms version.
    '''
    publish_ombuild_cmd = 'build-all-platforms'

class NoopBuild  ( GeneralBuild ):
    def __init__(self, options, path, cache, top_level):
        ''' Simplified build object with no implementations.  '''
        GeneralBuild.__init__(self, options, path, cache, top_level)

        # most of these command just call reombuild with the cmd
        self.configure = self.noop
        self.build = self.noop
        self.static_analysis = self.noop
        self.install = self.noop
        self.clean = self.noop
        self.distclean = self.noop

    def noop(self, cmd):
        pass

def read_build_conf_file(options, path, cache, top_level):
    ''' read the buildconf.py file for this module '''
    buildinfo = {}
    file_to_read = os.path.join(path, 'buildconf.py')
    execfile(file_to_read, globals(), buildinfo)
    bld = buildinfo['ComponentBuild'](options, path, cache, top_level)
    return bld

if __name__ == "__main__":
    sys.exit("no main implemented")
