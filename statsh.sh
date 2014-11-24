#!/bin/bash
echo "!/bin/bash" > tt.sh
git status . >> tt.sh
chmod +x tt.sh
cp tt.sh tttemp
cat tttemp | sed -e 's/^/#/' > tt.sh
rm tttemp
gvim --remote-tab tt.sh
