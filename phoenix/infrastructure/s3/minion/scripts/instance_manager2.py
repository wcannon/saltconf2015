#!/usr/bin/env python
import sys
import time
import datetime 
import logging
from dynamodb_mapper.model import utc_tz
import ddb
from ddb import MinionInstance
from ddb import MasterInstance
from msg2 import Msg
from sqs2 import Sqs
from key_manager import KeyManager
from helper2 import Helper


POLL_CYCLE = 15 # seconds to sleep between polling dynamodb for list of active salt masters
MASTERS_TABLE_NAME = "masters"
MINIONS_TABLE_NAME = "minions"
MASTER_QUEUE = "SqsMaster"
MINION_QUEUE = "SqsMinion"


class MasterManager:                                                                                                    
    def __init__(self, region):
        self.region = region
        ddb.set_region(self.region)

    def create_or_update_master(self, instanceid, modified, ipaddr, active):
        '''Attempt to retrieve the item update and save it, failing that create it and save it'''
        # no default value for instanceid, has be supplied
        if not instanceid:
            raise
        try:
            r = ddb.MasterInstance.get(instanceid)
            if r:
                print "Entry exists for instanceid %s" % instanceid
                if modified:
                    r.modified = modified
                if ipaddr:
                    r.ipaddr = ipaddr
                if active:
                    r.active = active
                r.save()
            else:  # no entry yet, let's make one
                print "Entry does not exist for instanceid %s, creating one." % instanceid
                mm = MasterInstance()
                mm.instanceid = instanceid
                if modified:
                    mm.modified = modified
                if ipaddr:
                    mm.ipaddr = ipaddr
                if active:
                    mm.active = active
                mm.save()
        except Exception, e:
            raise
        return

    def get_terminated(self):
        pass

class MinionManager:                                                                                                    
    def __init__(self, regin):
        self.region = region
        ddb.set_region(self.region)

    def create_or_update_minion(self, instanceid, modified, highstate_ran, highstate_runner, status):
        pass

    def get_terminated(self):
        '''Scan the dynamodb table for all minions with status == terminated, return list'''
        mm = MinionInstance()
        terminated_minions = []
        try:
            minions = mm.scan()
            for m in minions:
                if m.status == 'terminated':
                    terminated_minions.append(str(m.instanceid))
        except Exception, e:
            raise
        return terminated_minions

''' # Remove minion keys from my local salt master if their status is not active in dynamodb
    def terminate_minion(self, instanceid):
        pass
'''

def update_local_sm_info():
    pass

def main():
    # getting local info from ha-config file
    try:
        h = Helper()
        region = h.get_region()
        instanceid = h.get_instanceid()
        ipaddr = h.get_private_ip()
        master_queue = h.get_master_queue_name()
        minion_queue = h.get_minion_queue_name()
        master_table = h.get_master_table_name() 
        minion_table = h.get_minion_table_name()
        print "region: %s" % region
        print "instanceid: %s" % instanceid
        print "ipaddr: %s" % ipaddr
        print "master_queue: %s" % master_queue
        print "minion_queue: %s" % minion_queue
        print "master_table: %s" % master_table
        print "minion_table: %s" % minion_table
    except Exception, e:
        raise

    try:
        modified = datetime.datetime.now(utc_tz)
        local_master = MasterManager(region)
        local_master.create_or_update_master(instanceid=instanceid, modified=modified,
                                             ipaddr=ipaddr, active=True)
    except Exception, e:
        raise
       
    # get info to use from ha config file
    # update local salt master info in dynamodb
    # BIG LOOP
        # poll masters sqs queue
        # update dynamodb master table
        # update dynamodb minion table with master entry
        # poll minion sqs queue
        # update minion dynamodb table
        # retrieve terminated minions from dynamodb table, and remove their salt keys from local master
        # sleep the poll cycle time

  


if __name__ == "__main__":
    try:
        main()
    except Exception, e:
        print "Problem occurred.   %s" % e
