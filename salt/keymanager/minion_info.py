#!/usr/bin/env python
import os
import sys
import yaml
import logging
from salt.key import Key

log = logging.getLogger(__name__)
MINION_INFO_FILE =     "/etc/salt/ha/aws-autoscaling-info/aws_minions.yaml"
MINION_INFO_TMP_FILE = "/etc/salt/ha/aws-autoscaling-info/aws_minions.yaml.tmp"


def write_minion_file(minions_list):
  try:
    f = open(MINION_INFO_TMP_FILE, 'w')
    f.write(yaml.dump(minions_list))
    f.flush() 
    os.fsync(f.fileno())
    f.close()
    os.rename(MINION_INFO_TMP_FILE, MINION_INFO_FILE)
  except Exception, e:
    log.error("Exception: %s" % e)
    print "Problem writing minions file: %s" % e
    raise 
  return

def read_minion_file(file_path=MINION_INFO_FILE):
  '''Load in the minions info'''
  minions = []
  try:
    minions = yaml.load(open(file_path, "r").read())
  except Exception, e:
    # handling situation where the file does not exist
    minions = []
    #f = open(MINION_INFO_FILE, 'a')
    #f.write(yaml.dump(minions))
    #f.close()
    #log.error("Exception: %s" % e)
  return minions

def print_minions():
  minions = read_minion_file()
  print "MINIONS:"
  for m in minions:
    print m
  return

def add_minion_entry(item):
  try:
    minions = read_minion_file()
    if item not in minions:
      minions.append(item)
      write_minion_file(minions)
  except Exception, e:
    print "Exception: %s" % e 
    log.error("Exception: %s" % e)
    raise
  return 

def remove_minion_entry(item):
  try:
    minions = read_minion_file()
    minions.remove(item)
    write_minion_file(minions)
  except Exception, e:
    # if the value was not in the list we don't panic
    log.error("Exception: %s" % e)
  return 

def get_minion_id_by_instance_id(instance_id):
  '''Lookup a minion_id by searching through the list of minions
     Return the minion_id, or None if not found'''
  minions = read_minion_file()
  minion_id = None
  for m in minions:
    #print m
    if m.get('instance_id', None) == instance_id:
      minion_id = m.get('minion_id', None)
      break
  return minion_id 

def get_item_by_instance_id(instance_id):
  '''Lookup a minion_id by searching through the list of minions
     Return the minion_id, or None if not found'''
  minions = read_minion_file()
  minion = None
  for m in minions:
    #print m
    if m.get('instance_id', None) == instance_id:
      minion = m
      break
  return minion


if __name__ == "__main__":
  '''
  try:
    print "Reading minion file\n"
    x = read_minion_file()
    print x
  except Exception, e:
    print "Error reading minion file\n"
    print e
  try:
    print "Writing minion file\n"
    print write_minion_file(x)
  except Exception, e:
    print "Error reading minion file"
    print e
  '''
  #instance_id = sys.argv[1]
  #minion_id = get_minion_id_by_instance_id(instance_id)
  #print "Minion_ID for instance is: %s" % minion_id
  #add_minion_entry({'instance_id':'magic', 'minion_id':'cool-minion-2'})
  #print_minions()
  #remove_minion_entry({'instance_id':'magic', 'minion_id':'cool-minion-2'})

  ###print_minions()
  print
  print "Contents of minions file:"
  print print_minions()
  print "One instance: %s" % get_item_by_instance_id('i-4e087261')
  


