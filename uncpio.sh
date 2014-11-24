#!/bin/sh
cd __Build_8280__/binaries/
sudo mkdir tmp
cd tmp/
sudo gunzip -c ../initramfs.cpio.gz | sudo cpio -idv
cd ../../..
