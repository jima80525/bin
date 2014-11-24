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
            buildinfo = {}
            confFileName = os.path.join(root, "buildconf.py")
            execfile(confFileName, dict(), buildinfo) # second param is ignored by us
            conf = ''
            for cmd in buildinfo['buildCmd']:
                if cmd.startswith('rm'):
                    if cmd not in rms:
                        rms[cmd] = list()
                    rms[cmd].append(root)
                else:
                    if '-Dbuild.configurations=' in cmd:
                        # get configs in ombuild line
                        _, _, right = cmd.partition('-Dbuild.configurations=')
                        cfgs, _, _ = right.partition(' ')
                        const_cfgs = set(cfgs.split(','))

                        # get the configs specifiec in the buildconf.py file and
                        # make sure they are the same
                        spec_cfgs = set(buildinfo['configs'])
                        if const_cfgs != spec_cfgs:
                            print "%s config matching:"%root, const_cfgs.symmetric_difference(spec_cfgs)

                        # test to see if cfgs contain a product build if it also
                        # contains build-all-platforms AND if it does not
                        # contain a product it only has build-all
                        products = set(['maxwell_8280', 'maxwell_9280',
                                        'ambarella_amb_s2'])
                        if const_cfgs.intersection(products):
                            if not 'build-all-platforms' in cmd:
                                print "%s FAILED: product cfg without build-all-platforms command" % root
                        else:
                            if 'build-all-platforms' in cmd:
                                print "%s FAILED: NOT product cfg with build-all-platforms command" % root
                            elif 'build-all' not in cmd:
                                print "%s FAILED: command wihtout build-all" % root


                    conf += ':' + cmd



            #conf = ':'.join(buildinfo['buildCmd'])
            if conf not in confs:
                confs[conf] = list()
            confs[conf].append(root)

    for k,v in confs.items():
        print k, v

    print
    print "REMOVES"
    print
    for k,v in rms.items():
        print k, v
convertComponents(os.getcwd())


