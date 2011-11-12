#!/bin/sh

killall radvd

./ra-server -P 162 --radvd-path /usr/sbin/radvd \
            --radvd-an1-pidfile /var/run/radvd-an1.pid \
            --radvd-an2-pidfile /var/run/radvd-an2.pid \
            --an1 -C /etc/radvd-an1.conf -m stderr_syslog -p /var/run/radvd-an1.pid -s \
	    --an2 -C /etc/radvd-an2.conf -m stderr_syslog -m stderr_syslog -p /var/run/radvd-an2.pid -s
