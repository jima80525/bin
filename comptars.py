#!/usr/bin/env python3
import os
import subprocess
import sys

def get_tar_list(tarname):
    info = str(subprocess.check_output(['tar', '-tvf', tarname]))
    info = info.split('\\n')
    items = list()
    for line in info:
        if "'" != line:
            parts = line.split()
            if len(parts) > 5:
                (perms, owner, size, date, time, name, *rest) = parts
                link = None
                if perms.startswith('b'):
                    perms = perms[2:]
                if rest:
                    link = rest[1]
                items.append((perms, owner, size, name, link))
    return items

def compare_tars(goodtar, badtar):
    good = get_tar_list(goodtar)
    good.sort()
    bad = get_tar_list(badtar)
    bad.sort()
    for index, item in enumerate(bad):
        found = False
        if item not in good:
            for g in good:
                if g[3] == item[3]:
                    found = True
                    (gperms, gowner, gsize, gname, grest) = g
                    (perms, owner, size, name, rest) = item
                    if perms == gperms and owner == gowner and rest == grest:
                        diff = int(gsize) - int(size)
                        if diff > 10000:
                            print("Size mismatch {0}:G{1} B{2} diff:{3}".format(name, gsize, size, diff))
                    else:
                        print("MISMATCH FOUND", item)
                        print('(good version)', g)
            if not found and not item[3].endswith('/'):
                print("Found extra file", item[3])


def specific_comp():
    goodbase = '.depends'
    badbase = '/home/jima/work/remove_ant/external-3rdparty'
    pkgs = [
        # ( 'systemd/0.37-accept4', 'systemd_pkg-i686.tgz' ),
        # ( 'luaunit/1.3/', 'lua-unit_pkg-i686.tgz' ),
        # ( 'glibc/1.0.0/', 'glibc_pkg-i686.tgz' ),
        # ( 'cajun/2.0.2/', 'cajun_dev-pkg-i686.tgz' ),
        # ( 'dbus/1.4.16/', 'dbus_dev-pkg-i686.tgz' ),
        # ( 'dbus/1.4.16/', 'dbus_pkg-i686.tgz' ),
        # ( 'i2c-tools/3.0.2/', 'i2c-tools_pkg-i686.tgz' ),
        # ( 'shadow/4.1.5.1/', 'shadow_pkg-i686.tgz' ),
        # ( 'wpa_supplicant/2.6', 'wpa_supplicant_pkg-i686.tgz' ),
        # ( 'libcap/2.20', 'libcap_dev-pkg-i686.tgz' ),
        # ( 'libcap/2.20', 'libcap_pkg-i686.tgz' ),
        # ( 'timer_entropyd/0.1', 'timer_entropyd_pkg-i686.tgz' ),
        # ( 'dropbear/2012.55', 'dropbear_pkg-i686.tgz' ),
        # ( 'net-snmp/5.4.2', 'net-snmp_dev-pkg-i686.tgz' ),
        # ( 'net-snmp/5.4.2', 'net-snmp_pkg-i686.tgz' ),
        # ( 'fcgi/2.4.0', 'fcgi_dev-pkg-i686.tgz' ),
        # ( 'fcgi/2.4.0', 'fcgi_pkg-i686.tgz' ),
        # ( 'busybox/1.20.2', 'busybox_pkg-i686.tgz' ),
        # ( 'libjpeg-turbo/1.1.90', 'libjpeg-turbo_dev-pkg-i686.tgz' ),
        # ( 'libjpeg-turbo/1.1.90', 'libjpeg-turbo_pkg-i686.tgz' ),

        # ( 'ambarella_kernel/4.0.0', 'ambarella-kernel_dev-pkg-9340.tgz' ),
        # ( 'ambarella_kernel/4.0.0', 'ambarella-kernel_pkg-9340.tgz' ),
        ( 'ambarella_kernel/5.0.0', 'ambarella-kernel_dev-pkg-9500.tgz' ),
        ( 'ambarella_kernel/5.0.0', 'ambarella-kernel_pkg-9500.tgz' ),



    ]
    for (lib, pkg) in pkgs:
        goodname = os.path.join(goodbase, pkg)
        badname = os.path.join(badbase, lib, '.publish', pkg)
        print()
        print("GOOD:", goodname)
        print("BAD: ", badname)
        # compare_tars(goodname, badname)
        # compare_tars(badname, goodname)

    goodname = '.depends/omons-codegen_dev-pkg-amb_s2e.tgz'
    badname =  '/home/jima/work/remove_ant/omons/omons-codegen/.publish/omons-codegen_dev-pkg-amb_s2e.tgz'
    compare_tars(goodname, badname)

def comp_two_full_dirs():
    dir_one = '/home/jima/work/omons/products/9090/.depends'
    dir_two = '/home/jima/work/remove_ant/products/9090/.depends'
    for target in os.listdir(dir_one):
        if target.endswith('.tgz'):
            good = os.path.join(dir_one, target)
            bad = os.path.join(dir_two, target)
            print("GOOD: %s, BAD %s" % (good, bad))
            compare_tars(good, bad)


comp_two_full_dirs()
# x = get_tar_list('/home/jima/work/remove_ant/products/9090/.depends/wpa_supplicant_pkg-hi_3519.tgz')
# for item in x:
    # print(item)

