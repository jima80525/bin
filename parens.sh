#!/bin/sh
/home/jima/bin/remove_tabs.sh

find . -name '*.cpp' | xargs sed -i 's/( /(/g'
find . -name '*.h' | xargs sed -i 's/( /(/g'

find . -name '*.cpp' | xargs sed -i 's/ )/)/g'
find . -name '*.h' | xargs sed -i 's/ )/)/g'

