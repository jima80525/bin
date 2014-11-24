#!/bin/sh
find . -name '*[cpp|h]' ! -type d -exec bash -c 'expand -t 4 "$0" > /tmp/e && mv /tmp/e "$0"' {} \;
find . -name '*[cpp|h]' | xargs sed -i 's/if(/if (/g'
find . -name '*[cpp|h]' | xargs sed -i 's/for(/for (/g'
find . -name '*[cpp|h]' | xargs sed -i 's/i=0/i = 0/g'
find . -name '*[cpp|h]' | xargs sed -i 's/j=0/j = 0/g'
find . -name '*[cpp|h]' | xargs sed -i 's/y=0/y = 0/g'
find . -name '*[cpp|h]' | xargs sed -i 's/TRUE/true/g'
find . -name '*[cpp|h]' | xargs sed -i 's/FALSE/false/g'
find . -name '*[cpp|h]' | xargs sed -i 's/BYTE/uint8_t/g'
find . -name '*[cpp|h]' | xargs sed -i 's/UINT8/uint8_t/g'
find . -name '*[cpp|h]' | xargs sed -i 's/UINT/uint32_t/g'
find . -name '*[cpp|h]' | xargs sed -i 's/ABS/abs/g'
find . -name '*[cpp|h]' | xargs sed -i 's/SINT/uint16_t/g'
find . -name '*[cpp|h]' | xargs sed -i 's/\/sizeof/ \/ sizeof/g'
find . -name '*.cpp|h]' | xargs sed -i 's/BOOL/bool/g'

