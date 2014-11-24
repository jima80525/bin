#!/usr/bin/python
"""
Implements the artifact cache for the mh build system.
"""
import logging, sys, os, shutil
from git import *
from mhutils import *

class Cache:
    ''' Class to manage the local and remote artifact caches. '''
    def __init__(self, search=True, remote_publish=False):
        self.allow_local_search   = search
        self.allow_remote_search  = search
        self.allow_local_publish  = True # JHA for now always allow local pub
        self.allow_remote_publish = remote_publish
        self.server = "builder@fcbuildmaster.pelco.org"
        self.server_path = "/var/www/html/artifacts/omons/"
        self.local_cache_path = os.path.join(os.path.expanduser("~"),
                                            "build_cache/omons/")

    def perform_ssh_command(self, command):
        ''' Do the given ssh command '''
        return shell_cmd("/usr/bin/ssh %s \"%s\""%(self.server, command))

    def perform_scp_command(self, src_path, dst_path):
        ''' Do the given scp command '''
        return shell_cmd("/usr/bin/scp -q %s %s"%(src_path, dst_path))

    def search(self, dst_dir):
        ''' Search local and remote caches for artifact matching the required
        sha. '''
        dst_remote_dir = os.path.join(self.server_path, dst_dir)
        target = os.path.join(self.local_cache_path, dst_dir)

        if self.allow_local_search:
            if os.path.isdir(target):
                return True

        if self.allow_remote_search:
            # now check for the existence of the files
            if self.perform_ssh_command("stat %s >& /dev/null" % \
                                        dst_remote_dir) == 0:
                # the directory exists. Copy it to local cache
                if not os.path.isdir(target):
                    os.makedirs(target)

                self.perform_scp_command(self.server+":"+dst_remote_dir+"/*",
                                       target)
                return True

        return False

    def copy_from_cache(self, dst_dir, cache_dst_dir, configurations):
        """ Copy the files into the destination directory """

        conf_lookups = {
            'dm81xx'           : [ 'dm81xx', 'pelco_maxwell' ],
            'x86'              : [ 'x86' ],
            'ambs2'            : [ 'ambs2' ],
            'maxwell_8280'     : [ 'maxwell_8280', 'dm81xx', 'pelco_maxwell' ],
            'maxwell_9280'     : [ 'maxwell_9280', 'dm81xx', 'pelco_maxwell' ],
            'ambarella_amb_s2' : [ 'ambarella_amb_s2', 'dm81xx',
                                  'pelco_maxwell' ],
            'bigsur'           : [ 'bigsur', 'ambs2' ],
            'PC_x86'           : [ 'PC_x86', 'x86' ],
            'pelco_maxwell'    : [ 'pelco_maxwell' ],
        }

        target = os.path.join(self.local_cache_path, dst_dir)

        for entry in configurations:
            # Make the output dir if needed
            conf_dir = os.path.join(cache_dst_dir, entry)
            if not os.path.isdir(conf_dir):
                os.makedirs(conf_dir)

            # JHA TODO FIX THIS
            # rats.  Need to special case omons-lsp as maps to dm81xx.
            # This tells it to copy the maxwell_8280 target to the dm81xx
            # directory
            if 'omons-lsp' in target:
                entry = 'maxwell_8280'

            # now scan the list and copy files to the dest
            for (root, _, files) in os.walk(target):
                for name in files:
                    for conf_name in conf_lookups[entry]:
                        if conf_name in name or name.endswith('.txt'):
                            logging.debug("copying %s to %s",
                                          os.path.join(root, name), conf_dir)
                            shutil.copy(os.path.join(root, name), conf_dir)

    def publish(self, src_dir, dst_dir):
        ''' Copy the artifact to the allowed cache(s). '''
        if self.allow_remote_publish:
            # copy files up to remote server
            remote_dir = os.path.join(self.server_path, dst_dir)
            self.perform_ssh_command("mkdir -p "+ remote_dir)
            self.perform_scp_command(src_dir + "/*", self.server+":"+remote_dir)

        if self.allow_local_publish:
            # copy files to local cache
            target = os.path.join(self.local_cache_path, dst_dir)
            shutil.rmtree(target, True) # remove pre-existing cache for this sha
            shutil.copytree(src_dir, target)

if __name__ == "__main__":
    sys.exit("no main implemented")

