#!/bin/bash
#sed -i "s/'amb_s2', 'linaro'/'linaro'/" `find . -name buildconf.py`
#grep "configs =" `find . -name buildconf.py` | sed "s/^.*:    //" | sort | uniq > dump
grep "configs =" `find . -name buildconf.py` | sed "s/^.*:    //" | sort | uniq > dump
#grep "configs =" `find . -name buildconf.py` > dump
#perl -e "s/omons/fred/" tt
