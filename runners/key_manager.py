#!/usr/bin/env python
import sys
import salt
import salt.client
from salt.key import Key


opts = salt.config.master_config('/etc/salt/master')
mymanager = Key(opts)

def manage(miniondata="no miniondata passed"):
  minion_id = str( miniondata['id'] )
  if minion_id = "ip-10-0-10-137.ec2.internal":
    accept_key(minion_id)
  return

def delete_key(minion_id):
  mymanager = Key(opts)
  mymanager.delete_key(minion_id)
  return

def accept_key(minion_id):
  mymanager = Key(opts)
  mymanager.accept(match=minion_id)
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
  
  print "\nList of all accepted keys:"
  minions = get_current_minions()
  print (", ").join(minions) 

  # example accept
  if minion_id:
    accept_key(minion_id)

  # example delete
  #if minion_id:
  #  delete_key(minion_id)


  print "\nList of all accepted keys:"
  minions = get_current_minions()
  print (", ").join(minions) 
