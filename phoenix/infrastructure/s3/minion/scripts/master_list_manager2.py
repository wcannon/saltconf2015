#!/usr/bin/env python
import sys
import yaml
import time
import helper
import subprocess
import ddb
import salt
from helper2 import Helper

POLL_CYCLE = 10
CONFIG_FILE = "/etc/salt/minion"
SVC_NAME = "salt-minion"

class MasterListManager:
    

    def __init__(self, poll_cycle=None, config_file=None, table_name=None, svc_name=None ):
        if not poll_cycle:
            self.poll_cycle = POLL_CYCLE
        if not config_file:
            self.config_file = CONFIG_FILE
        if not table_name:
            h = Helper()
            table_name = h.get_master_queue_name()
            self.table_name = table_name
        if not svc_name:
            self.svc_name = SVC_NAME

    def get_current_salt_masters(self):
      '''retrieve and return the list of current salt masters out of the minion config file'''
      try:
          info_yaml = yaml.load(open(self.config_file, "r").read())
          masters = info_yaml.get('master', [])
      except Exception, e:
          raise
      return masters

    def get_active_salt_masters(self):
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

    def update_config(self, masters_list, config_file=None):
      '''update CONFIG_FILE with active salt masters if needed'''
      if not config_file:
          config_file = self.CONFIG_FILE
      try:
          info_yaml = yaml.load(open(config_file, "r").read())
          info_yaml['master'] = masters_list
          with open(config_file, 'w') as yaml_file:
              yaml_file.write( yaml.dump (info_yaml, default_flow_style=False))
      except Exception, e:
          raise
      return

    def restart_local_minion(self):
      '''restart the local salt-minion service'''
      result = False
      try:
          output = subprocess.check_output(["/usr/sbin/service", SVC_NAME, "restart"])
          # print "restarting service - %s" % SVC_NAME
      except:
          # print "Exception when restarting service [%s] status" % SVC_NAME
          raise
      return

    def main(self):
      try:
          region = helper.get_region()
          ddb.set_region(region)
      except Exception, e:
          print "Exception: %s" % e
          sys.exit(1) 
      while True:
          try:
              print "zone is: %s" % region
              local_sm_list = self.get_current_salt_masters()
              print "local_sm_list is: %s" % local_sm_list
          except Exception, e:
              print "Unable to get current salt masters from minion config"
              print e
              raise
          
          try:
              dynamodb_sm_list = self.get_active_salt_masters()
              # print "dynamodb_sm_list is: %s" % dynamodb_sm_list
              if set(local_sm_list) != set(dynamodb_sm_list): # are lists unequal
                  #  print "lists don't match...updating config and restarting minion"
                  self.update_config(masters_list=dynamodb_sm_list)
                  self.restart_local_minion()
              else:
                  pass
                  # print "lists match, sleeping"
          except Exception, e:
               raise
          time.sleep(self.poll_cycle)

if __name__ == "__main__":
  m = MasterListManager()
  try:
    m.main()
  except Exception, e:
    print "Unable to manage the master list for this minion: %s" % e
    sys.exit(1)
