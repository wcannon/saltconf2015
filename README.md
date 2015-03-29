# Phoenix

There is now one solution (solution three) aka The Phoenix. 

In this project every salt-master runs a salt-minion.  This allows an administrator to log onto any salt master and run states / execution modules against all servers.

AutoScaling groups launch new salt masters and minions as needed.  

The salt masters list and salt minions list are now fully dynamic, with data about both stored in dynamodb.

Minions monitor the list of masters in dynamodb, updating their own config file with the masters list if it does not match those found in dynamodb, followed by a restart of the salt-minion service.  This makes it trivial to have minions switch from one master to another, or to follow several masters as needed.

Amazon AWS services used:
CloudFormation
IAM
S3
SNS
SQS
Dynamodb
AutoScaling
VPC + subnets, security groups and etc.

Minion Key Management is done by:
Salt Reactor and Custom Salt-Runner key_runner.py

Minion highstate is done by:
Salt Reactor and Custom Salt-Runner highstate_runner.py

Instance/Minion list in dynamodb managed by:
Custom Code - instance_manager.py

Master list updated on minions managed by:
Custom Code - master_list_manager.py
