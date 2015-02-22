#!/usr/bin/env python
import os
import logging

log = logging.getLogger(__name__)
MINION_INFO_FILE = "/etc/salt/ha/aws-autoscaling-info/aws_minions.yaml"
MINION_INFO_TMP_FILE = "/etc/salt/ha/aws-autoscaling-info/aws_minions.yaml.tmp"


def read_minion_file(myfile=MINION_INFO_FILE):
  pass

def write_minion_file(minions_yaml):
  try:
    f = open(MINION_INFO_TMP_FILE, 'w')
    f.write(yaml.dump(minions_yaml))
    f.flush() 
    os.fsync(f.fileno())
    f.close()
    os.rename(MINION_INFO_TMP_FILE, MINION_INFO_FILE)
  except Exception, e:
    log.error("Exception: %s" % e)
    raise 
  return

def get_minion_info():
  '''Retrieve minion info list of dicts and return them'''
  return read_minoin_file()

def get_minion_info(file_path=MINION_INFO_FILE):
  '''Load in the minions info'''
  minions = []
  try:
    mydict = yaml.load(open(file_path, "r").read())
    minions = mydict.get('minions', [])
  except Exception, e:
    print "Unable to open file, or convert to dict, giving an empty dict"
    log.error("Exception: %s" % e)
    raise
  return minions

def add_minion_entry(item):
  try:
    minions = get_minion_info()
    minions.append(item)
    write_minion_file(minions)
  except Exception, e:
    print "Exception: %s" % e 
    log.error("Exception: %s" % e)
    raise
  return 

def remove_minion_entry(item):
  pass

def get_minion_id_by_instance_id(instance_id):
  pass

