#!/bin/bash
# script does ack on a string and opens a new tab in gvim for each file with matches
/usr/bin/ack-grep -l $* > tt.sh
# first prepend the command to open vim.  not pretty
cat tt.sh | sed -e 's:^:/usr/bin/vi --servername GVIM --remote-tab :' >> tttemp
# now we need to work around a bug (?) in gvim where calling --remote-tab several times
# quickly causes it to open them in the same window, not in new tabs
# so we sleep between each call
cat tttemp | sed -e '/^/a \
sleep 0.1 ' > tttemp2
# remove last sleep from the file and move back to tt.sh
head -n -1 tttemp2 > tt.sh
#  remove temp files
rm tttemp*
chmod +x tt.sh
. tt.sh
rm tt.sh

