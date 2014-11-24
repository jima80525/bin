#!/usr/bin/python
from optparse import OptionParser
from xml.dom.minidom import parse, parseString

def parseAssembly(afile):
    dom1 = parse(afile) # parse an XML file by name
    manifest = dom1.getElementsByTagName("manifest")[0]
    ombuilds = manifest.getElementsByTagName("ombuild")
    rpms = manifest.getElementsByTagName("rpm")
    ll = []
    for comp in ombuilds:
        a = comp.attributes['repo'].value
        #print a
        if 'omons-micro' in a:
            name = a.split('/')[-2]
            if 'trunk' in name: name = a.split('/')[-3]
            if 'aduc7020'    in name: name = 'motordownload'
            ll.append(name)
        elif 'omons-fpga' in a:
            ll.append(a.split('/')[-3])
        else:
            #print a.split('/')[-1]
            #ll.append(a.split('/')[-1])
            name = a.split('/')[-1]
            if 'wide-dhcpv6' in name: name = 'dhcpv6'
            if 'fne-porting' in name: name = 'fne'
            if 'WebUI'       in name: name = 'webui'
            ll.append(name)
    for comp in rpms:
        a = comp.attributes['spec'].value
        name = a.split('/')[-1]
        if 'boot'            in name: name = 'u-boot'
        if 'mobi-csp'        in name: name = 'mobi-csp'
        if 'fpga-obscura'    in name: name = 'evo'
        if 'ccp-mg3264'      in name: name = 'ccp-mg3264'
        if 'fpga.spec'       in name: name = 'serdes'
        if 'fpga-ipipe-bits' in name: name = 'lamar-bits'
        if 'fpga-ipipe-lib'  in name: name = 'lamar-lib'
        if 'fwupdate'     in name: continue
        if 'finalize'     in name: continue
        ll.append(name)
    ll.sort()
    return ll

def parseIvy(ifile):
    dom1 = parse(ifile) # parse an XML file by name
    deps = dom1.getElementsByTagName("dependencies")[0]
    comps = deps.getElementsByTagName("dependency")
    #print comps
    ll = []
    for comp in comps:
        a = comp.attributes['name'].value
        if 'evo_hawk' in a: a = 'evo'
        if 'flex' in a or 'omons_platform' in a:
            continue
        ll.append(a)
    ll.sort()
    return ll

def compareSets(set1, set2, msg):
    missing = []
    for l in set1:
        if l not in set2:
            if 'i2c-tools' not in l:
                missing.append(l)
    if missing:
        print msg
        print "________________________________________"
        for m in missing:
            print m
        print

def getFilenamesFromCommandLine():
    (_, args) = OptionParser().parse_args()
    assemblyfile = args[0] or "assembly.xml"
    ivyfile = args[1] or "ivy.xml"
    print assemblyfile + "\t" + ivyfile
    return (assemblyfile, ivyfile)

(assemblyfile, ivyfile) = getFilenamesFromCommandLine()
asset = set(parseAssembly(assemblyfile))
ivyset = set(parseIvy(ivyfile))
compareSets(asset, ivyset, "In assembly.xml and not ivy.xml:")
compareSets(ivyset, asset, "In ivy.xml and not assembly.xml:")
