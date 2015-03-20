#!/usr/bin/env python
import sys
import ddb
import msg
import sqs
import key_deleter
import time
import helper

POLL_CYCLE = 60 # seconds to sleep between polling dynamodb for list of active salt masters
MASTERS_TABLE_NAME = "masters"
MINIONS_TABLE_NAME = "minions"
MASTER_QUEUE = "SqsMaster"
MINION_QUEUE = "SqsMinion"


def create_master(instanceid, ipaddr, active):
  '''if an item exists in the masters table for this server, update it, otherwise create one'''
  ### Neds to be updated
  result = False
  try:
    a = ddb.MasterInstance()
    masters = a.scan()
    for m in masters:
      if m.active == True:
         master_ipaddrs.append(str(m.ipaddr))
  except Exception, e:
    raise
  return result

def update_master(instanceid, ipaddr, active):
  '''if an item exists in the masters table for this server, update it, otherwise create one'''
  ### Neds to be updated
  result = False
  try:
    a = ddb.MasterInstance()
    masters = a.scan()
    for m in masters:
      if m.active == True:
         master_ipaddrs.append(str(m.ipaddr))
  except Exception, e:
    raise
  return result

def create_minion(instanceid, ipaddr, active):
  '''if an item exists in the masters table for this server, update it, otherwise create one'''
  ### Neds to be updated
  result = False
  try:
    a = ddb.MasterInstance()
    masters = a.scan()
    for m in masters:
      if m.active == True:
         master_ipaddrs.append(str(m.ipaddr))
  except Exception, e:
    raise
  return result

def update_minion(instanceid, ipaddr, active):
  '''if an item exists in the masters table for this server, update it, otherwise create one'''
  ### Neds to be updated
  result = False
  try:
    a = ddb.MasterInstance()
    masters = a.scan()
    for m in masters:
      if m.active == True:
         master_ipaddrs.append(str(m.ipaddr))
  except Exception, e:
    raise
  return result

def remove_terminated_minion_keys():
  '''Get list of terminated minions from minions table
     if an instanceid/minionid is in the local salt masters keys,
     delete the key'''
  pass

def main():
  try:
    instanceid = helper.get_instanceid()
    region = helper.get_region()
    ipaddr = helper_get_private_ip()
    ddb.set_region(region)
    ## set my ip address in the masters table
  except Exception, e:
    print "Unable to get necessary info, exiting: %s" % e
    sys.exit(1)
  
  while True:
    ## poll masters sqs queue, update masters table, and minions table
    try:
      sqs_conn = sqs.get_connection(region)
      num_sqs_messages = sqs.get_queue_length(sqs_conn, MASTER_QUEUE)
      for m in range(num_sqs_messages):
        message = sqs.get_a_message(sqs_conn, queue)
        # if launch, add to masters, add to minions
        # if terminate, update masters, update minions
    except Exception, e:
      print "Problem with master queue management: %s" % e
      raise

    ## poll minions sqs queue, update minions table
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
    time.sleep(POLL_CYCLE)

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
