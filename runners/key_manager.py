#!/usr/bin/env python
import sys
import salt
import yaml
import salt.client
from salt.key import Key


opts = salt.config.master_config('/etc/salt/master')
mymanager = Key(opts)
aws_minion_file = "/etc/salt/ha/aws-autoscaling-info/aws_minion_info.yaml"

'''  Reference of yaml on aws_minion_file
minions:
  - minion:
      minion_id: ip-10-0-10-137.ec2.internal
      key_action: accept  # accept | delete  | reject
      instance_id: i-4e087261
'''

def load_minion_info(file_path=aws_minion_file):
  mydict = [] # useful if sns/sqs have not provided any info = no minion file yet
  mystr = "no data"
  try:
    mydict = yaml.load(open(file_path, "r").read())
    minions = mydict.get('minions', [])
  except Exception, e:
    print "Unable to open file, or convert to dict, giving an empty dict"
    print "Exception: %s" % e
    print "mystr = %s" % mystr
    print "mydict %s" % mydict
    raise
  return minions

def get_key_action_for_minion(minion_list, minion_id):
  '''If we don't find the key, return None, else return whatever the action
     is as the value of 'key_action' '''
  print type(minion_list)
  key_action = None
  for anitem in minion_list:
    item = anitem['minion'] 
    mid = item.get('minion_id', 'no-id')
    if mid == minion_id:
      action = item.get('key_action', None)
      key_action = action
  return key_action

def manage(miniondata="no miniondata passed"):
  minion_id = str( miniondata['id'] )
  minion_list = load_minion_info(aws_minion_file)
  key_action = get_key_action_for_minion(minion_list, minion_id)
  if not key_action:  # minion id not found in our lookup list
    reject_key(minion_id)
  
  if key_action == 'accept': # new expected minion from aws autoscaling
    accept_key(minion_id)
  elif key_action == 'delete': # minion is being terminated by aws autoscaling
    delete_key(minion_id)
  else:
    mystr = "nothing to do here"
  return

def test_manage(minion_id):
  minion_list = load_minion_info(aws_minion_file)
  key_action = get_key_action_for_minion(minion_list, minion_id)
  if not key_action:  # minion id not found in our lookup list
    reject_key(minion_id)

  if key_action == 'accept': # new expected minion from aws autoscaling
    accept_key(minion_id)
  elif key_action == 'delete': # minion is being terminated by aws autoscaling
    delete_key(minion_id)
  else:
    mystr = "nothing to do here"
  return

def delete_key(minion_id):
  mymanager = Key(opts)
  mymanager.delete_key(minion_id)
  return

def accept_key(minion_id):
  mymanager = Key(opts)
  mymanager.accept(match=minion_id)
  return

def reject_key(minion_id):
  mymanager = Key(opts)
  mymanager.reject(match=minion_id)
  return


def get_pending_keys():
  mymanager = Key(opts)
  keys = mymanager.list_keys()
  return keys['minions_pre']

def get_current_minions():
  mymanager = Key(opts)
  keys = mymanager.list_keys()
  return keys['minions']

def has_minion_key_arrived(minion_id):
  status = False
  arrived = get_pending_keys()
  if minion_id in arrived:
    status =  True
  return status


if __name__ == "__main__":

  minion_id = None
  if len(sys.argv) > 1:
   minion_id = sys.argv[1]
  
  #print "\nList of all accepted keys:"
  #minions = get_current_minions()
  #print (", ").join(minions) 

  # example accept
  if minion_id:
    test_manage(minion_id)

  # example delete
  #if minion_id:
  #  delete_key(minion_id)


  print "\nList of all accepted keys:"
  minions = get_current_minions()
  print (", ").join(minions) 
