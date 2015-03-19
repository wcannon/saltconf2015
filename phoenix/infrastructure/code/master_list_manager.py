#!/usr/bin/env python
import sys
import yaml
import time
import subprocess
from ddb import MasterInstance

POLLCYCLE = 60 # seconds to sleep between polling dynamodb for list of active salt masters
CONFIG_FILE = "/etc/salt/minion"
TABLE_NAME = "masters"
SVC_NAME = "salt-minion"

def get_current_salt_masters(config_file=CONFIG_FILE):
  '''retrieve and return the list of current salt masters out of the minion config file'''
  masters = []
  try:
    info_yaml = yaml.load(open(config_file, "r").read())
    masters = info_yaml.get('master', None)
  except Exception, e:
    raise
  return masters

def get_active_salt_masters():
  '''retrieve and return the list of active salt masters from dynamodb'''
  master_ipaddrs = []
  try:
    a = MasterInstance()
    masters = a.scan()
    for m in masters:
      if m.active == True:
         master_ipaddrs.append(m.ipaddr)
  except Exception, e:
    raise
  return master_ipaddrs

def update_config(masters_list, config_file=CONFIG_FILE):
  '''update CONFIG_FILE with active salt masters if needed'''
  try:
    info_yaml = yaml.load(open(config_file, "r").read())
    info_yaml['master'] = masters_list
    stream = file(config_file, 'w')
    yaml.dump(info_yaml, stream)
  except Exception, e:
    raise
  return

def restart_local_minion():
  '''restart the local salt-minion service'''
  result = False
  try:
    output = subprocess.check_output(["/usr/sbin/service", SVC_NAME, "restart"])
    print "restarting service - %s" % svc_name
  except:
    print "Exception when restarting service [%s] status" % svc_name
    raise
  return

def main():
  try:
    local_sm_list = get_current_salt_masters()
  except Exception, e:
    print "Unable to get current salt masters from minion config"
    print e
    raise
  dynamodb_sm_list = get_active_salt_masters()
  if local_sm_list != dynamodb_sm_list: # are lists unequal
    update_config(masters_list=dynamodb_sm_list)
    restart_local_minion()
  time.sleep(POLL_CYCLE)

def main2():
  try:
    masters = get_active_salt_masters()
    print "masters in dynamodb are: %s" % masters
  except Exception, e:
    print "Problem fetching masters from dynamodb: %s" % e
    raise

if __name__ == "__main__":
  try:
    #main()
    main2()
  except Exception, e:
    print "Unable to execute properly: %s" % e
    sys.exit(1)
