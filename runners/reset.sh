#!/bin/bash

service salt-master restart
rm /root/most_recent_salt_highstate_run.txt
rm /tmp/highstate-data
rm /tmp/highstate_runner
salt-key -y -D
service salt-minion restart
