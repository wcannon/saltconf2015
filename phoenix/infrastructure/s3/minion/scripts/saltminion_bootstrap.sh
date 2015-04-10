#!/bin/bash

# set up ppa for saltstack
add-apt-repository -y ppa:saltstack/salt
apt-get update

# install salt-minion
apt-get install -y salt-minion

# download minion config file -- contains a 'master: 127.0.0.1 record' and other
# necessary info e.g. file_roots, custom modules and etc
aws s3 cp s3://saltconf2015-solution-2/minion/minion_config /etc/salt/minion

## Replace the standard minion id with the aws instance-id -- guaranteed to be globally unique
instanceid=`curl -s http://169.254.169.254/latest/meta-data/instance-id`
echo "id: $instanceid" >> /etc/salt/minion

service salt-minion restart

aws s3 cp s3://saltconf2015-solution-2/aws_scripts/restart_bc_dns.py /etc/salt/restart_bc_dns.py
chmod +x /etc/salt/restart_bc_dns.py
echo "PATH=/usr/bin:/bin:/sbin" >> /var/spool/cron/crontabs/root
echo "* * * * * /usr/bin/python /etc/salt/restart_bc_dns.py" >> /var/spool/cron/crontabs/root

