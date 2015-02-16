#!/bin/bash

# set up ppa for saltstack
add-apt-repository -y ppa:saltstack/salt
apt-get update

# install salt-minion
apt-get install -y salt-minion

# download minion config file -- contains a 'master: 127.0.0.1 record' and other
# necessary info e.g. file_roots, custom modules and etc
aws s3 cp s3://saltconf2015bucket/minions_config /etc/salt/minion

# download grains file - contains info about self (e.g. administration role)
aws s3 cp s3://saltconf2015bucket/webserver-grains /etc/salt/grains

service salt-minion restart

# the plan is for the minion key to be sent to the master
# a reactor on the master either rejects the key and discards it
# or accepts the key and instructs the minion to run a highstate
