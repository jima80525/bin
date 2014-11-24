#!/bin/bash
#sed -i "s/'8280', '9280', 'PC', '8360'/'8280', '9280', '8360', 'PC'/" `find . -name buildconf.py`
#sed -i "s/^    configs = \[ '8280', '9280',  ]/    configs = \[ '8280', '9280', ]/" `find . -name buildconf.py`
sed -i "s/^    configs = \[ 'dm81xx', 'linaro', 'x86', ]/    configs = \[ 'arago', 'linaro', 'gcc_x86', ]/" `find . -name buildconf.py`
sed -i "s/^    configs = \[ 'dm81xx', 'linaro', ]/    configs = \[ 'arago', 'linaro', ]/" `find . -name buildconf.py`
sed -i "s/^    configs = \[ 'dm81xx', ]/    configs = \[ 'arago', ]/" `find . -name buildconf.py`
sed -i "s/^    configs = \[ 'x86', ]/    configs = \[ 'gcc_x86', ]/" `find . -name buildconf.py`
#sed -i "s/^    configs = \[ 'x86','dm81xx', 'amb_s2', 'linaro' ]/    configs = \[ 'dm81xx', 'linaro', 'x86', ]/" `find . -name buildconf.py`
#sed -i "s/^    configs = \[ '8280', '9280', 'PC', '8360' ]/    configs = \[ '8280', '8360', '9280', '9340', 'amb_evm', 'PC', 'wooff', ]/" `find . -name buildconf.py`
#sed -i "s/^    configs = \[ 'bigsur', '8360','PC','8280','9280', '8360' ]/    configs = \[ '8280', '8360', '9280', '9340', 'amb_evm', 'PC', 'wooff', ]/" `find . -name buildconf.py`
#sed -i "s/^    configs = \[ 'bigsur','PC','8280','9280', '8360'  ]/    configs = \[ '8280', '8360', '9280', '9340', 'amb_evm', 'PC', 'wooff', ]/" `find . -name buildconf.py`
#sed -i "s/^    configs = \[ 'bigsur','PC','8280','9280','8360' ]/    configs = \[ '8280', '8360', '9280', '9340', 'amb_evm', 'PC', 'wooff', ]/" `find . -name buildconf.py`
#sed -i "s/^    configs = \[ 'PC', '8280', '9280', 'bigsur', '8360' ]/    configs = \[ '8280', '8360', '9280', '9340', 'amb_evm', 'PC', 'wooff', ]/" `find . -name buildconf.py`
#grep "configs =" `find . -name buildconf.py` > dump
#perl -e "s/omons/fred/" tt
