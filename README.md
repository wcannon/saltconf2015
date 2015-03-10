# saltconf2015
Open Source code for my SaltConf 2015 Talk

Two "high availability" solutions are provided.

Update:  This week I'm changing a lot of this code.  I'll be moving the minion_db file to dyanmodb.  I'll also stop relying on dns for minions to find the masters.  This will also now be captured in dynamodb.  

To summarize:  the various solutions are being combined into one solution.  The number of salt masters will vary by changing the cloudformation template launch group for salt masters.  
