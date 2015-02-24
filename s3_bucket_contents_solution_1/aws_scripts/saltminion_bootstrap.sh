#!/bin/bash

# set up ppa for saltstack
add-apt-repository -y ppa:saltstack/salt
apt-get update

# install salt-minion
apt-get install -y salt-minion

# download minion config file -- contains a 'master: 127.0.0.1 record' and other
# necessary info e.g. file_roots, custom modules and etc
aws s3 cp s3://saltconf2015-solution-1/minion/minion_config /etc/salt/minion

# download grains file - contains info about self (e.g. administration role)
aws s3 cp s3://saltconf2015-solution-1/minion/webserver-grains /etc/salt/grains

service salt-minion restart

aws s3 cp s3://saltconf2015-solution-1/aws_scripts/restart_salt_minion.py /etc/salt/restart_salt_minion.py
chmod +x /etc/salt/restart_salt_minion.py
echo "PATH=/usr/bin:/bin:/sbin" >> /var/spool/cron/crontabs/root
echo "*/3 * * * * /usr/bin/python /etc/salt/restart_salt_minion.py" >> /var/spool/cron/crontabs/root
