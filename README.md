# Phoenix

This repository contains software for a new open source project - Phoenix.  The objective of this project is to make it relatively easy to run SaltStack in a highly available manner in the AWS cloud.  

When a salt master is terminated it should be replaced automatically, picking up where it left off.  When the population of salt masters changes minions automatically update their list of salt masters and restart their salt-minion service.  

In this project every salt-master runs a salt-minion.  This allows an administrator to log onto one salt master and run states / execution modules against all servers.

AutoScaling groups launch new salt masters and minions as needed, according to auto-scaling policies.  

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

NOTE:  Due to how saltstack handles multi-master minion connections the default minion config uses a setting "master_type: failover".  The net effect is that all minions use one salt-master.  When that master becomes unavailable they switch to the next master in listed in the minion config file, trying each master listed until working successfully with a master.  The list of masters in the minion config file is maintained by master_list_manager.py, run as an ubuntu startup script.  It produces an ordered list from the dynamodb masters table.
