#!/usr/bin/env python
import sys
import sqs
import msg
import time
import salt
import yaml
from salt.key import Key


opts = salt.config.master_config('/etc/salt/master')
mymanager = Key(opts)
aws_minion_file = "/etc/salt/ha/aws-autoscaling-info/aws_minion_info.yaml"
aws_ha_config_file = "/etc/salt/ha/ha-config"


def load_ha_config_info(file_path=aws_ha_config_file):
  '''This provides access to info such as region, queue_name for
     connecting to sqs and ec2'''
  mydict = {} # useful if sns/sqs have not provided any info = no minion file yet
  try:
    mydict = yaml.load(open(file_path, "r").read())
  except Exception, e:
    print "Exception: %s" % e
    raise
  return mydict

def load_minion_info(file_path=aws_minion_file):
  '''We maintain this list - minions whose key should be accepted by salt-master when submitted'''
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

def delete_key(minion_id):
  mymanager = Key(opts)
  mymanager.delete_key(minion_id)
  return

if __name__ == "__main__":
  try:
    config_info = load_ha_config_info()
    print "region: %s" % config_info.get('region', 'no-region-found')
    print "queue_name: %s" % config_info.get('queue_name', 'no-queue_name-found')
  except:
    print "Unable to open ha-config or read it correctly."
    sys.exit(1)

  try:
    minions = load_minion_info()
    for m in minions:
      print m
  except:
    print "Unable to load minions file."
    sys.exit(1)

'''
   The general loop
  	get a message from sqs
	extract info from message
	if Launch:
		lookup minion-id in ec2
		append minion-id , instance-id to minion info file
		delete message from sqs queue
        if Terminate:
		lookup minion-id in minion info file
		remove minion-id , instance-id from minion info file
		delete key from salt-master
'''

'''
  try:
    messages = sqs.main(region, queue_name)
    print "Received %s messages" % len(messages)
    new_messages_list = []
    now = time.time()
    for m in messages:
      #print "\n\nmessage body:"
      #print m.get_body()
      action = msg.get_instance_action(m.get_body())
      #print "action: %s" % action
      instance_id = msg.get_instance_id(m.get_body())
      #print "instance_id: %s" % instance_id
      event = {}
      #event['status'] = "open"
      event['instance_id'] = instance_id
      event['action'] = action
      event['time'] = now # seconds since epoch - when retrieving messages
      # add later event['highstate_status'] = 
      event['minion_id'] = '' # placeholder
      new_messages_list.append(event)
    for event in new_messages_list:
      print event
  except:
    print "Unable to retrieve sqs messages"
'''
  

