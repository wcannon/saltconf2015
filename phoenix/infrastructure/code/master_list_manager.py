#!/usr/bin/env python
import sys
import yaml
import time
import helper
import subprocess
import ddb

POLL_CYCLE = 10 # seconds to sleep between polling dynamodb for list of active salt masters
CONFIG_FILE = "/etc/salt/minion"
TABLE_NAME = "masters"
SVC_NAME = "salt-minion"

def get_current_salt_masters(config_file=CONFIG_FILE):
  '''retrieve and return the list of current salt masters out of the minion config file'''
  masters= []
  try:
    info_yaml = yaml.load(open(config_file, "r").read())
    masters = info_yaml.get('master', [])
  except Exception, e:
    raise
  return masters

def get_active_salt_masters():
  '''retrieve and return the list of active salt masters from dynamodb'''
  master_ipaddrs = []
  try:
    a = ddb.MasterInstance()
    masters = a.scan()
    for m in masters:
      if m.active == True:
         master_ipaddrs.append(str(m.ipaddr))
  except Exception, e:
    raise
  return master_ipaddrs

def update_config(masters_list, config_file=CONFIG_FILE):
  '''update CONFIG_FILE with active salt masters if needed'''
  try:
    info_yaml = yaml.load(open(config_file, "r").read())
    print 
    print "info yaml contains: %s" % info_yaml
    print
    info_yaml['master'] = masters_list
    with open(config_file, 'w') as yaml_file:
      yaml_file.write( yaml.dump (info_yaml, default_flow_style=False))
  except Exception, e:
    raise
  return

def restart_local_minion():
  '''restart the local salt-minion service'''
  result = False
  try:
    output = subprocess.check_output(["/usr/sbin/service", SVC_NAME, "restart"])
    print "restarting service - %s" % SVC_NAME
  except:
    print "Exception when restarting service [%s] status" % SVC_NAME
    raise
  return

def main():
  try:
    region = helper.get_region()
    ddb.set_region(region)
  except Exception, e:
    print "Exception: %s" % e
    sys.exit(1) 
  while True:
    try:
      print "zone is: %s" % region
      local_sm_list = get_current_salt_masters()
      print "local_sm_list is: %s" % local_sm_list
    except Exception, e:
      print "Unable to get current salt masters from minion config"
      print e
      raise
  
    dynamodb_sm_list = get_active_salt_masters()
    print "dynamodb_sm_list is: %s" % dynamodb_sm_list
    if set(local_sm_list) != set(dynamodb_sm_list): # are lists unequal
      print "lists don't match...updating config and restarting minion"
      update_config(masters_list=dynamodb_sm_list)
      restart_local_minion()
    else:
      print "lists match, sleeping"
    print "sleeping for %s seconds" % POLL_CYCLE
    time.sleep(POLL_CYCLE)

if __name__ == "__main__":
  try:
    main()
  except Exception, e:
    print "Unable to execute properly: %s" % e
    sys.exit(1)
