#!/bin/sh

PORT=3000
# use smaller length for larger scans
# docker performs very poorly so this should be close to 26 or something
# this scans 62 addresses which should be sufficient
PREFIX_LENGTH=26

# get the local ip of the eth0 interface and add the prefix length to it
# the value of this variable should look like: 192.168.0.2/26
IP_RANGE="$(ip -o addr show eth0 | awk '{print $4}' | cut -d/ -f1 | tr -d [\(\)])/$PREFIX_LENGTH"

# the output looks like:
# 192.168.0.4 (hostname1)
# 192.168.0.3 (hostname2)
nmap -oG - -sS -p $PORT $IP_RANGE | awk '/open/{print $2 " " $3}'

