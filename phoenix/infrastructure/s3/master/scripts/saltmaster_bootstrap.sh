#!/bin/bash
## This script should install the saltstack master, and then call the bootstrap script for the saltstack minion

# These parameters are passed in via aws auto scaling
bucketname=$1
region=$2
queuename_minion=$3
queuename_master=$4
grainsfile=$5

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

# set up expected HA dir 
mkdir -p /etc/salt/ha

# populate ha config file with info needed by runner, and keymanager
echo "bucket_name: $bucketname" >> /etc/salt/ha/ha-config
echo "region: $region" >> /etc/salt/ha/ha-config
echo "queuename_minion: $queuename_minion" >> /etc/salt/ha/ha-config
echo "queuename_master: $queuename_master" >> /etc/salt/ha/ha-config

# Check to see if our saltmaster.pem file exists by doing a simple ls on the expected location
# If not, we are the first saltmster, and will push our keys into the bucket
info=`aws s3 ls s3://$bucketname/master/master.pem 2>/dev/null`

if [ $? -eq 0 ]
then
  ## if the key exists, download it and restart salt-master service
  #echo "found key in s3, downloading and restarting salt-master"
  service salt-master stop
  aws s3 cp s3://$bucketname/master/master.pem /etc/salt/pki/master/master.pem
  aws s3 cp s3://$bucketname/master/master.pub /etc/salt/pki/master/master.pub
  service salt-master start 
else 
  ## key does not exist, upload our key as we are the first salt-master
  #echo "key not found in s3, uploading master key to s3"
  aws s3 cp /etc/salt/pki/master/master.pem s3://$bucketname/master/master.pem
  aws s3 cp /etc/salt/pki/master/master.pub s3://$bucketname/master/master.pub
fi

# Need to git clone the repo locally so that a highstate can run on the salt-master
git clone https://github.com/wcannon/saltconf2015.git  /root/saltconf2015

# Copy in master config
aws s3 cp s3://$bucketname/master/config/saltmaster_config /etc/salt/master

# create symlinks
ln -s /root/saltconf2015/phoenix/pillar /srv/pillar
ln -s /root/saltconf2015/phoenix/salt /srv/salt
ln -s /root/saltconf2015/phoenix/salt/reactor /srv/reactor
ln -s /root/saltconf2015/phoenix/salt/runners /srv/salt/runners

# restart salt-master to pick up any master config file changes
service salt-master restart

## Instead of installing salt-minion & etc, we download the minion bootstrap
## and run it passing in params just like any minion receives
aws s3 cp s3://$bucketname/minion/scripts/saltminion_bootstrap.py .
chmod +x saltminion_bootstrap.py
/usr/bin/python ./saltminion_bootstrap.py $bucketname $grainsfile

# get our instanceid
myid='curl http://169.254.169.254/latest/meta-data/instance-id/'

# accept our minion key
salt-key -y -a $myid

# run local highstate
salt-call --local state.highstate

# Download instance_manager.py
mkdir -p /usr/local/bin/phoenix
aws s3 cp s3://$bucketname/minion/scripts/instance_manager.py /usr/local/bin/phoenix
aws s3 cp s3://$bucketname/minion/scripts/instance_manager.conf /etc/init/instance_manager.conf
chmod +x /usr/local/bin/phoenix/instance_manager.py

# start the instance_manager service
service instance_manager start
