#!/bin/bash

# expecting region as param 1
region=$1
# expecting the dns name for the server as well
dnsname=$2
# queuename
queuename=$3


instancedns=`curl -s http://169.254.169.254/latest/meta-data/public-hostname`

## Update our template rrset dns batch change file
aws s3 cp s3://saltconf2015-solution-1/master/rrset_template.json /tmp
#sed  "s/new-dns-name/sol1-salt1.devopslogic.com/" rrset_template.json | sed "s/target-dns-name/ec2.1234awsdns.com/" > rrset2.json
sed  "s/new-dns-name/$dnsname/" /tmp/rrset_template.json | sed "s/target-dns-name/$instancedns/" > /tmp/rrset2.json

# Create / Update record for sol1-salt1.devopslogic.com
#aws --region us-east-1 route53 change-resource-record-sets --hosted-zone-id Z2IBYTQ6W9V2HA --change-batch file:///root/rrset2.json
aws --region us-east-1 route53 change-resource-record-sets --hosted-zone-id Z2IBYTQ6W9V2HA --change-batch file:///tmp/rrset2.json

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

# set up expected HA dirs - 
mkdir -p /etc/salt/ha/{runner-output,aws-autoscaling-info}

# populate ha config file with info needed by runner, and keymanager
echo "queue_name: $queuename" >> /etc/salt/ha/ha-config
echo "region: $region" >> /etc/salt/ha/ha-config
echo "dns_name: $dnsname" >> /etc/salt/ha/ha-config


# Check to see if our saltmaster.pem file exists by doing a simple ls on the expected location
info=`aws s3 ls s3://saltconf2015-solution-1/master/master.pem 2>/dev/null`

if [ $? -eq 0 ]
then
  ## if the key exists, download it and restart salt-master service
  #echo $?
  #echo "found key in s3, downloading and restarting salt-master"
  service salt-master stop
  aws s3 cp s3://saltconf2015-solution-1/master/master.pem /etc/salt/pki/master/master.pem
  aws s3 cp s3://saltconf2015-solution-1/master/master.pub /etc/salt/pki/master/master.pub
  service salt-master start 
else 
  ## key does not exist, upload our key as we are the first salt-master
  #echo $?
  #echo "key not found in s3, uploading master key to s3"
  aws s3 cp /etc/salt/pki/master/master.pem s3://saltconf2015-solution-1/master/master.pem
  aws s3 cp /etc/salt/pki/master/master.pub s3://saltconf2015-solution-1/master/master.pub
fi


# download master config file
aws s3 cp s3://saltconf2015-solution-1/master/saltmaster_config  /etc/salt/master

# download salt cloud config file
aws s3 cp s3://saltconf2015-solution-1/master/ec2.conf  /etc/salt/cloud.providers.d/ec2.conf

# Need to git clone the repo locally so that a highstate can run on the salt-master
git clone https://github.com/wcannon/saltconf2015.git  /root/saltconf2015

# create symlinks
ln -s /root/saltconf2015/pillar /srv/pillar
ln -s /root/saltconf2015/reactor /srv/reactor
ln -s /root/saltconf2015/salt /srv/salt
ln -s /root/saltconf2015/runners /srv/salt/runners

# restart salt-master to pick up any master config file changes
service salt-master restart

# install salt-minion
apt-get install -y salt-minion

# download minion config file -- contains a 'master: 127.0.0.1 record' and other
# necessary info
aws s3 cp s3://saltconf2015-solution-1/master/saltmaster_minion_config  /etc/salt/minion

# download grains file - contains info about self (e.g. administration role)
aws s3 cp s3://saltconf2015-solution-1/master/saltmaster-grains  /etc/salt/grains

service salt-minion restart

# Accept the master's key on itself
sleep 15s
salt-key -y -A

# Run a highstate on local master
salt-call --local state.highstate
