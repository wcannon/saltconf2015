#!/usr/bin/env python
import sys
import ddb
import msg
import sqs
import key_deleter
import time
import helper

POLL_CYCLE = 15 # seconds to sleep between polling dynamodb for list of active salt masters
MASTERS_TABLE_NAME = "masters"
MINIONS_TABLE_NAME = "minions"
MASTER_QUEUE = "SqsMaster"
MINION_QUEUE = "SqsMinion"


def create_master(region, instanceid, ipaddr=None, active=None):
  '''if an item exists in the masters table for this server, update it, otherwise create one'''
  result = False
  try:
    ddb.set_region(region)
    a = ddb.MasterInstance()
    a.instanceid = instanceid
    if ipaddr:
      a.ipaddr = ipaddr
    if active:
      a.active = active
    a.save()
  except Exception, e:
    raise
  return result

def update_master(region=None, instanceid=None, ipaddr=None, active=None):
  '''if an item exists in the masters table for this server, update it, otherwise return False'''
  result = False
  try:
    ddb.set_region(region)
    a = ddb.MasterInstance.get(instanceid)
    if instanceid:
      a.instanceid = instanceid
    if ipaddr:
      a.ipaddr = ipaddr
    if active:
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

def get_terminated_minions(region):
  '''Scan the dynamodb table for all minions
     Return a list of those that have status not set to terminated'''
  '''retrieve and return the list of active salt masters from dynamodb'''
  instanceid_list = []
  ddb.set_region(region)
  try:
    a = ddb.MinionInstance()
    minions = a.scan()
    for m in minions:
      if m.status == 'terminated':
         instanceid_list.append(str(m.instanceid))
  except Exception, e:
    raise
  return instanceid_list

def remove_terminated_minions(instance_ids):
  '''Given a list of instance id, remove their key from the local salt master'''
  result = True
  try:
    if instance_ids:
      for i in instance_ids:
        key_deleter.delete_key(i)
  except Exception, e:
    result = False
    print "Error deleting key: %s" % e
    pass
  return result

  
def main():
  try:
    info = sqs.load_ha_config_info()
    queue_master = info['queuename_master']
    queue_minion = info['queuename_minion']
    region = info['region']
    instanceid = helper.get_instanceid()
    region = helper.get_region()
    ipaddr = helper.get_private_ip()
    ddb.set_region(region)
    sqs_conn = sqs.get_connection(region)
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

  pass_no = 0 
  while True:
    ## poll masters sqs queue, update masters table, and minions table
    pass_no += 1
    print "pass # %s" % pass_no
    try:
      num_sqs_messages = sqs.get_queue_length(sqs_conn, queue_master)
      print "Number of messages in master queue: %s" % num_sqs_messages
      for m in range(num_sqs_messages):
        message = sqs.get_a_message(sqs_conn, queue_master)
        instanceid = msg.get_instance_id(message)
        print "MASTER: instanceid = %s" % instanceid
        action = msg.get_instance_action(message)
        print "MASTER: action = %s" % instanceid
        if "LAUNCH" in action:
          create_master(region=region, instanceid=instanceid)
          create_minion(region=region, instanceid=instanceid, modified=None, highstate_ran=False,
                        highstate_runner=None, status="active")
        elif "TERMINATE" in action:
          update_master(region=region, instanceid=instanceid, active=False)
          update_minion(region=region, instanceid=instanceid, modified=None, highstate_ran=None,
                        highstate_runner=None, status="terminated")
        # Removing the message from the queue so that it does not repopulate automatically
        sqs.delete_a_message(sqs_conn, queue_master, message)
    except Exception, e:
      print "Problem with master queue management: %s" % e
      raise

    ## poll minions sqs queue, update minions table
    try:
      num_sqs_messages = sqs.get_queue_length(sqs_conn, queue_minion)
      print "Number of messages in minion queue: %s" % num_sqs_messages
      for m in range(num_sqs_messages):
        message = sqs.get_a_message(sqs_conn, queue_minion)
        instanceid = msg.get_instance_id(message)
        print "MINION: instanceid = %s" % instanceid
        action = msg.get_instance_action(message)
        print "MINION: action = %s" % action
        if "LAUNCH" in action:
          create_minion(region=region, instanceid=instanceid, modified=None, highstate_ran=False,
                        highstate_runner=None, status="active")
        elif "TERMINATE" in action:
          update_minion(region=region, instanceid=instanceid, modified=None, highstate_ran=None,
                        highstate_runner=None, status="terminated")
        # Removing the message from the queue so that it does not repopulate automatically
        sqs.delete_a_message(sqs_conn, queue_minion, message)
    except Exception, e:
      print "Problem with minion queue management: %s" % e
      raise

    ## get a list of all minions which are terminated
    try:
      result = False
      instance_ids = get_terminated_minions(region)
      result = remove_terminated_minions(instance_ids)
    except Exception, e:
      print "Error occurred: %s" % e
      raise
    
    time.sleep(POLL_CYCLE)

if __name__ == "__main__":
  try:
    main()
  except Exception, e:
    print "Exception occurred: %s" % e
