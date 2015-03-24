#!/usr/bin/env python
import sys
import ddb
import msg
import sqs
import key_deleter
import time
import helper

POLL_CYCLE = 31 # seconds to sleep between polling dynamodb for list of active salt masters
MASTERS_TABLE_NAME = "masters"
MINIONS_TABLE_NAME = "minions"
MASTER_QUEUE = "SqsMaster"
MINION_QUEUE = "SqsMinion"


def create_master(region, instanceid, ipaddr, active):
  '''if an item exists in the masters table for this server, update it, otherwise create one'''
  result = False
  try:
    ddb.set_region(region)
    a = ddb.MasterInstance()
    a.instanceid = instanceid
    a.ipaddr = ipaddr
    a.active = active
    a.save()
  except Exception, e:
    raise
  return result

def update_master(region, instanceid, ipaddr, active):
  '''if an item exists in the masters table for this server, update it, otherwise return False'''
  result = False
  try:
    ddb.set_region(region)
    a = ddb.MasterInstance.get(instanceid)
    a.instanceid = instanceid
    a.ipaddr = ipaddr
    a.active = active
    result = a.save()
  except Exception, e:
    pass
  return result

def create_minion(region, instanceid, modified=None, highstate_ran=None, highstate_runner=None, status=None):
  '''create a minion in the dynamodb table '''
  result = False
  try:
    ddb.set_region(region)
    a = ddb.MinionInstance()
    a.instanceid = instanceid
    if modified:
      a.modified = modified
    if highstate_ran:
      a.highstate_ran = highstate_ran
    if highstate_runner:
      a.highstate_runner = highstate_runner
    if status:
      a.status = status
    result = a.save()
  except Exception, e:
    pass
  return result

def update_minion(region, instanceid, modified=None, highstate_ran=None, highstate_runner=None, status=None):
  '''create a minion in the dynamodb table '''
  result = False
  try:
    ddb.set_region(region)
    a = ddb.MinionInstance.get(instanceid)
    if modified:
      a.modified = modified
    if highstate_ran:
      a.highstate_ran = highstate_ran
    if highstate_runner:
      a.highstate_runner = highstate_runner
    if status:
      a.status = status
    result = a.save()
  except Exception, e:
    pass
  return result

def remove_terminated_minion_keys():
  '''Get list of terminated minions from minions table
     if an instanceid/minionid is in the local salt masters keys,
     delete the key'''
  pass

def main():
  try:
    info = sqs.load_ha_config_info()
    queue_master = info['queuename_master']
    region = info['region']
    instanceid = helper.get_instanceid()
    region = helper.get_region()
    ipaddr = helper.get_private_ip()
    ddb.set_region(region)
    ## set my ip address in the masters table
  except Exception, e:
    print "Unable to get necessary info, exiting: %s" % e
    sys.exit(1)

  # Attempt to update our master entry, and create it if we can't update it
  try:  
    result = update_master(region, instanceid, ipaddr, active=True)
    if not result:
      create_master(region, instanceid, ipaddr, active=True)
  except Exception, e:
    raise  
 
  while True:
    ## poll masters sqs queue, update masters table, and minions table
    try:
      sqs_conn = sqs.get_connection(region)
      num_sqs_messages = sqs.get_queue_length(sqs_conn, queue_master)
      for m in range(num_sqs_messages):
        message = sqs.get_a_message(sqs_conn, queue_master)
        print message.__dict__
        print "----------------------------------------"
        print
        # if launch, add to masters, add to minions
        # if terminate, update masters, update minions
    except Exception, e:
      print "Problem with master queue management: %s" % e
      raise

    ## poll minions sqs queue, update minions table
    '''
    try:
      sqs_conn = sqs.get_connection(region)
      num_sqs_messages = sqs.get_queue_length(sqs_conn, MINION_QUEUE)
      for m in range(num_sqs_messages):
        message = sqs.get_a_message(sqs_conn, queue)
        # if launch, add to minions
        # if terminate, update minions
    except Exception, e:
      print "Problem with minion queue management: %s" % e
      raise
    ## get a list of all minions which are terminated
    ## and remove keys from self salt.Key 
    '''
    time.sleep(POLL_CYCLE)

if __name__ == "__main__":
  try:
    main()
  except Exception, e:
    print "Exception occurred: %s" % e


'''
 - on loop e.g. once a minute
 - if salt-master is 'active', updates its 'active' state to true in dynamodb:masters table
 - polls master sqs queue
   - update dynamodb:minions table accordingly (add / delete)
     - get a list of all status==terminated minions, and ensure that their keys are not in salt.key
   - update dynamodb:masters table accordingly (but set active to false)
 - polls minion sqs queue
   - update dynamodb:minions table accordingly (add / delete)
 - this is how the ip address of a master gets updated in the masters table - updates its own ip address
 - it also updates the active to true after a highstate has been run on it
'''
