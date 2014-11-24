#!/bin/sh
echo $1
sudo rm -rf $1lib/modules/2.6.*/build
sudo rm -rf $1lib/modules/2.6.*/source
sudo rm -rf $1usr/src/kernel
sudo find . -name *.ko -delete
sudo find . -name *.so -delete
sudo find . -name *.so.* -delete
sudo find . -name .placeholder -delete
sudo find . -name *.pc -delete
sudo rm -rf $1codegen

