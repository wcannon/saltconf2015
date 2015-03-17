# Phoenix

There is now one solution (solution three) aka The Phoenix. 

In this project every salt-master runs a salt-minion.

AutoScaling groups launch new masters and minions as needed.  

The salt masters list and salt minions list are now fully dynamic, with data about both stored in dynamodb.

Minions monitor the list of masters in dynamodb, updating their own config file with the masters list if it does not match those found in dynamodb, followed by a restart of the salt-minion service.

The masters will now keep track of minion highstate status using a dynamodb table, including which master gets to run the highstate on a minion.

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
Salt Reactor and Custom Salt-Runner key_manager.py

Minion highstate is done by:
Salt Reactor and Custom Salt-Runner highstate_manager.py

Instance/Minion list in dynamodb managed by:
Custom Code - instance_manager.py

Master list updated on minions managed by:
Custom Code - master_list_manager.py
