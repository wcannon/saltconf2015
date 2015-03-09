# saltconf2015
Open Source code for my SaltConf 2015 Talk

Two "high availability" solutions are provided.

Each solution has an accompanying "how to" document.  

All code / solutions are contained in this github repository.

NOTE:  This code is considered a prototype, but a great start.

I am actively editing the code to improve the current issues:
1.  setting the minion names for non salt masters to be their aws instance-id values
2.  updating minion db modules to use the simplified instance-id values
3.  changed the cron for restarting minions to detect dns changes of salt masters, and restart the salt-minion when detected
4.  solution one is broken for now...will backport solutions of #2 into #1 when done testing
