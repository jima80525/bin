#!/bin/sh

rm -rf ./tmp
mkdir ./tmp
mv initramfs.cpio.gz ./tmp
#cp initramfs.cpio.gz ./tmp
cd tmp
gunzip initramfs.cpio.gz
cpio -idv < initramfs.cpio
ls
cd ..
