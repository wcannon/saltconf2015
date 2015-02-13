#!/bin/bash

# expecting region as param 1
region=$1
# expecting to receive the elastic ip allocation info as param
eip=$2

# Associate this ec2 instance with an elastic ip address
## Need local instance id
instanceid=`curl -s http://169.254.169.254/latest/meta-data/instance-id`
#echo $instanceid

## Need eip allocation id
aws ec2 associate-address  --region $region --allow-reassociation  --instance-id $instanceid  --allocation-id $eip
# e.g. aws --region us-west-2 ec2 associate-address  --allow-reassociation   --instance-id i-5731105b  --allocation-id eipalloc-2fcf1b4a

# set up ppa for saltstack
add-apt-repository -y ppa:saltstack/salt
apt-get update

# install some core components
apt-get install -y salt-syndic
apt-get install -y salt-cloud
apt-get install -y salt-ssh
apt-get install -y salt-api
apt-get install -y salt-doc

# install salt-master
apt-get install -y salt-master

# download master config file
aws s3 cp s3://saltconf2015bucket/masters_master_config /etc/salt/master

################################################################################
####### Need to git clone the repo locally so that a highstate can run #########
################################################################################
# git clone into local dir  /root/saltconf2015
git clone https://github.com/wcannon/saltconf2015.git

# create symlinks
#  pillar  reactor  README.md  s3_bucket_contents  salt
#ln -s /home/wcannon/saltconf2015/saltconf2015/salt /tmp/salt
ln -s /root/saltconf2015/pillar /srv/pillar
ln -s /root/saltconf2015/reactor /srv/reactor
ln -s /root/saltconf2015/salt /srv/salt

# restart salt-master to pick up any master config file changes
service salt-master restart

## If master encryption key already in S3 bucket, replace local key with it and restart salt-master
## If not, push the new master encryption key up to the S3 bucket

# install salt-minion
apt-get install -y salt-minion

# download minion config file -- contains a 'master: 127.0.0.1 record' and other
# necessary info e.g. file_roots, custom modules and etc
aws s3 cp s3://saltconf2015bucket/masters_minion_config /etc/salt/minion

# download grains file - contains info about self (e.g. administration role)
aws s3 cp s3://saltconf2015bucket/saltmaster-grains /etc/salt/grains

service salt-minion restart

# Accept the master's key on itself
sleep 15s
salt-key -y -A

# Run a highstate on local master
salt-call --local state.highstate
