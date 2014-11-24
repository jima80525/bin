#!/usr/bin/python
import sys
import struct

def getLong(f):
    a = f.read(1)
    b = f.read(1)
    c = f.read(1)
    d = f.read(1)
    x = struct.unpack('<HH',d+c+b+a)
    val = x[0] + (x[1] * 0xFFFF)
    return val

filenames = ['fwupdate1.scr',
             'fwupdate2.scr',
             'ubl',
             'uboot',
             'stdenv',
             'uImage',
             'rootnand']

try:
    imgfile = sys.argv[1]
except:
    exit("Must specify file to parse")

print "Processing: ", imgfile

with open(imgfile, "rb") as f:
    f.seek(64)
    info = list()
    currentStart = 0x60 # first image starts after header - TODO make this
                        # generic to handle case where we don't have exactly
                        # 7 sections.  Note that the filenames trick will die in
                        # that case, too.
    for filename in filenames:
        fileinfo = dict()
        fileinfo['name'] = filename
        fileinfo['length'] = getLong(f)
        fileinfo['start'] = currentStart
        currentStart += fileinfo['length']
        fileinfo['end'] = currentStart
        while currentStart % 4:
            currentStart += 1
        info.append(fileinfo)
    # OK, now we've got the info about each file, let's try to write out each
    # section
    for ii in info:
        f.seek(ii['start'])
        data = f.read(ii['length'])
        with open(imgfile + "-" + ii['name'], 'wb') as out:
            out.write(data)
            out.close()

# finally print out the report
print "filename      start     size        end"
for ii in info:
    print '{0:13s} {1:9s} {2:11s} {3:s}'.format(ii['name'], hex(ii['start']), hex(ii['length']), hex(ii['end']))
exit()

