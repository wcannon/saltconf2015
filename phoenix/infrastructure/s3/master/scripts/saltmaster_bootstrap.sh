#!/bin/bash
## This script should install the saltstack master, and then call the bootstrap script for the saltstack minion
## example run:  /saltmaster_bootstrap.sh hpulse-static-devops-bucket us-west-2  minions masters saltmaster  minions  masters  wcannon  'password1'  'DenisBajet/SuperDevops.git' wcannon  'password2'  'wcannon/devops-pillar.git'

# These parameters are passed in via aws auto scaling
bucketname=$1
region=$2
queuename_minion=$3
queuename_master=$4
grainsfile=$5
minion_table=$6
master_table=$7
states_git_user=$8
states_git_password=$9
states_git_url=${10}
pillar_git_user=${11}
pillar_git_password=${12}
pillar_git_url=${13}

#echo "bucketname: $bucketname"
#echo "region: $region"
#echo "minion queue: $queuename_minion"
#echo "master queue: $queuename_master"
#echo "grainsfile: $grainsfile"
#echo "minion_table: $minion_table"
#echo "master_table: $master_table"
#echo "states_git_user: $states_git_user"
#echo "states_git_password: $states_git_password"
#echo "states_git_url: $states_git_url"
#echo "pillar_git_user: $pillar_git_user"
#echo "pillar_git_password: $pillar_git_password"
#echo "pillar_git_url: $pillar_git_url"

#sleep 30
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
echo "minion_table: $minion_table" >> /etc/salt/ha/ha-config
echo "master_table: $master_table" >> /etc/salt/ha/ha-config
echo "states_git_user: $states_git_user" >> /etc/salt/ha/ha-config
echo "states_git_password: $states_git_password" >> /etc/salt/ha/ha-config
echo "states_git_url: $states_git_url" >> /etc/salt/ha/ha-config
echo "pillar_git_user: $pillar_git_user" >> /etc/salt/ha/ha-config
echo "pillar_git_passwrod: $pillar_git_password" >> /etc/salt/ha/ha-config
echo "pillar_git_url: $pillar_git_url" >> /etc/salt/ha/ha-config

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

# Need to git clone the states repo locally so that a highstate can run on the salt-master
git clone https://$states_git_user:$states_git_password@github.com/$states_git_url  /root/saltconf2015

# Need to git clone the pillar repo locally so that secrets and configs are available on the salt-master
git clone https://$pillar_git_user:$pillar_git_password@github.com/$pillar_git_url  /root/pillar

# Copy in master config
aws s3 cp s3://$bucketname/master/config/saltmaster_config /etc/salt/master

# create symlinks
ln -s /root/saltconf2015/pillar/ /srv/pillar
ln -s /root/saltconf2015/salt /srv/salt
ln -s /root/saltconf2015/salt/reactor/ /srv/reactor

# restart salt-master to pick up any master config file changes
service salt-master restart

## Instead of installing salt-minion & etc, we download the minion bootstrap
## and run it passing in params just like any minion receives
aws s3 cp s3://$bucketname/minion/scripts/saltminion_bootstrap.py .
chmod +x saltminion_bootstrap.py
/usr/bin/python ./saltminion_bootstrap.py $bucketname $grainsfile $master_table

# get our instanceid
myid='curl http://169.254.169.254/latest/meta-data/instance-id/'

# accept our minion key
salt-key -y -a $myid

# run local highstate
salt-call --local state.highstate

# Download instance_manager and other necessary classes
mkdir -p /usr/local/bin/phoenix
aws s3 cp s3://$bucketname/minion/scripts/sqs.py /usr/local/bin/phoenix
aws s3 cp s3://$bucketname/minion/scripts/helper.py /usr/local/bin/phoenix
aws s3 cp s3://$bucketname/minion/scripts/ddb.py /usr/local/bin/phoenix
aws s3 cp s3://$bucketname/minion/scripts/msg.py /usr/local/bin/phoenix
aws s3 cp s3://$bucketname/minion/scripts/key_manager.py /usr/local/bin/phoenix
aws s3 cp s3://$bucketname/minion/scripts/key_runner.py /usr/local/bin/phoenix
aws s3 cp s3://$bucketname/minion/scripts/highstate_runner.py /usr/local/bin/phoenix
aws s3 cp s3://$bucketname/minion/scripts/instance_manager.py /usr/local/bin/phoenix
aws s3 cp s3://$bucketname/minion/scripts/instance_manager.conf /etc/init/instance_manager.conf
chmod +x /usr/local/bin/phoenix/instance_manager.py

# start the instance_manager service
service instance_manager start
