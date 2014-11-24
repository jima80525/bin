#!/bin/sh
find . -name '*.cpp' | xargs sed -i '/\$Id/d'
find . -name '*.h' | xargs sed -i '/\$Id/d'
