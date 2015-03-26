#!/usr/bin/env python
import sys
import yaml
import time
import helper
import subprocess
import ddb


class MasterListManager:
    
    POLL_CYCLE = 10 
    CONFIG_FILE = "/etc/salt/minion"
    TABLE_NAME = "masters"
    SVC_NAME = "salt-minion"

    def __init__(self):
        self.opts = salt.config.master_config('/etc/salt/master')
        self.mymanager = Key(opts)

    def get_current_salt_masters(self, config_file=MasterListManager.CONFIG_FILE):
      '''retrieve and return the list of current salt masters out of the minion config file'''
      try:
          info_yaml = yaml.load(open(config_file, "r").read())
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

    def update_config(self, masters_list, config_file=MasterListManager.CONFIG_FILE):
      '''update CONFIG_FILE with active salt masters if needed'''
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
        time.sleep(POLL_CYCLE)

if __name__ == "__main__":
  m = MasterListManager()
  try:
    m.main()
  except Exception, e:
    print "Unable to manage the master list for this minion: %s" % e
    sys.exit(1)
