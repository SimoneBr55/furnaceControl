#!/bin/bash

#-----------------------------------------------------#
# logrotate.sh v1.0
# > Simone Brazioli
# Script to stash away the logs in a gz compressed file
#-----------------------------------------------------#
cd /home/pi/furnaceControl
cd oldlog
gzip -d dnsapi.ark.log.gz
cd /home/pi/furnaceControl
cat dnsapi.log >> oldlog/dnsapi.ark.log
truncate -s0 dnsapi.log
cd oldlog
gzip dnsapi.ark.log
exit 0

