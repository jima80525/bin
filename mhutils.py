#!/usr/bin/python
''' Utilities for mh build script. '''
import logging, sys, os, subprocess
import hashlib
#from mhbuild_classes import *
from git import *

def shell_cmd(cmd):
    ''' Utility to flush output streams before doing system call '''
    sys.stdout.flush()
    sys.stderr.flush()
    logging.debug("CMD: %s", cmd)
    return subprocess.call(cmd, shell=True)

_CODE_REPO = None
def get_code_repo():
    ''' Gets the repo for the code.  Uses global to only create heavy object
    once. '''
    global _CODE_REPO
    if _CODE_REPO == None:
        _CODE_REPO = Repo(os.getcwd())
    return _CODE_REPO

def get_script_version():
    ''' Gets the version of these scripts. '''
    # JHA TODO - change this into get sha for this dir
    return "0.5.0"

def get_sha_for_module(current_dir):
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
    repo = get_code_repo()
    base_dir = repo._working_tree_dir

    # run the status command with "-z -u all"
    stat = repo.git.status(current_dir, z=True, u='all')
    if not len(stat):
        # Nothing changed - use the git sha
        rel_path = os.path.relpath(current_dir, base_dir)
        tree = repo.head.commit.tree
        commit_sha = tree[rel_path].hexsha
        logging.debug("Sha pulled from GIT for %s: %s", current_dir,
                      commit_sha)
    else:
        # something changed on the local filesys.  Go through and compute the
        # hash of all the contents of all the files that have changed.  Note
        # that this will not track adding empty directories (who cares).
        logging.debug("output of git status: %s", stat)
        hasher = hashlib.sha1()
        for line in stat.split('\0'):
            if line: # z format returns an empty line at end
                _, filename = line.split()
                full_file_name = os.path.join(base_dir, filename)
                # only get the hash for actual files
                if os.path.isfile(full_file_name):
                    with open(full_file_name) as hash_file:
                        hasher.update(hash_file.read())

        commit_sha = hasher.hexdigest()
        logging.debug("Sha pulled from files for %s: %s", current_dir,
                      commit_sha)
    return commit_sha

# Get the version info for the Tools and cache this so we only have to construct
# that object once.
_TOOLS_VERSION = None
def get_tools_version():
    ''' Get the sha of the omtools. '''
    global _TOOLS_VERSION
    if _TOOLS_VERSION == None:
        tools_repo = Repo("/opt/omtools/")
        _TOOLS_VERSION = (u"omtools version: ", tools_repo.head.commit.hexsha)
    return _TOOLS_VERSION

def create_component_dir(module_path, subdir):
    """Creates the subdir for the given component and returns the full path to
    that subdir.  """
    fullpath = os.path.join(module_path, subdir)
    if not os.path.isdir(fullpath):
        os.makedirs(fullpath)
    return fullpath

if __name__ == "__main__":
    sys.exit("no main implemented")
