#!/bin/bash
echo N | sudo tee /sys/module/nfsd/parameters/nfs4_disable_idmapping
sudo systemctl restart nfs-kernel-server nfs-idmapd
