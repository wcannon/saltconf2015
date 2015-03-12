# saltconf2015
Open Source code for my SaltConf 2015 Talk

Two "high availability" solutions are provided.

Update:  This week I'm changing a lot of this code.  I'll be moving the minion_db file to dynamodb.  I'll also stop relying on dns for minions to find the masters.  This will also now be captured in dynamodb.  

To summarize:  the various solutions are being combined into one solution - solution three.  The number of salt masters will vary by changing the cloudformation template launch group for salt masters.  

The masters list will now be dynamic, not relying on fixed number of dns names.  Minions will detect a change in the masters list in, update their own config, and restart the salt-minion service.

The masters will now keep track of minion highstate status using a dynamodb table, including which master gets to run the highstate on a minion.

Solution three allows for a variable number of masters (1 - X), and a variable number of minions.  In addition new masters will be automatically added to minions, whereas retired masters will be automatically removed from minions.  
