#!/usr/bin/env python
import sys
import salt
import yaml
from salt.key import Key
import minion_info
import msg
import sqs
import ec2
import time
import key_deleter
import logging

log = logging.getLogger(__name__)
opts = salt.config.master_config('/etc/salt/master')
mymanager = Key(opts)
aws_minion_file = "/etc/salt/ha/aws-autoscaling-info/aws_minions.yaml"
aws_ha_config_file = "/etc/salt/ha/ha-config"
SLEEPTIME = 10


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

def loop():
  try:
    config_info = load_ha_config_info()
    region = config_info.get('region', 'no-region-found')
    #print "region: %s" % region
    queue = config_info.get('queue_name', 'no-queue_name-found')
    #print "queue: %s" % queue
  except:
    print "Unable to open ha-config or read it correctly."
    sys.exit(1)

  try:
    sqs_conn = sqs.get_connection(region)
    num_sqs_messages = sqs.get_queue_length(sqs_conn, queue)
    #print "Number of messages to process: %s" % num_sqs_messages
    for m in range(num_sqs_messages):
      message = sqs.get_a_message(sqs_conn, queue)
      #sqs.print_message(message)
      if message:
        instance_id = msg.get_instance_id(message)
        #print "instance_id: %s" % instance_id
        action = msg.get_instance_action(message)
        #action = msg.get_body(message)
        #print "action: %s" % action
        #if action == "autoscaling::EC2_INSTANCE_LAUNCH":
        #if action.find("autoscaling::EC2_INSTANCE_LAUNCH") != -1:
        ec2_conn = ec2.get_connection(region)
        if action and action.find("LAUNCH") != -1:
          #print "connecting to ec2"
          minion_id = ec2.get_private_dns_name(ec2_conn, instance_id)
          #print "minion_id: %s" % minion_id
          item = {'instance_id':str(instance_id), 'minion_id':str(minion_id)}
          minion_info.add_minion_entry(item)
        #elif action == "autoscaling::ECW_INSTANCE_TERMINATE":
        #elif action == "autoscaling::ECW_INSTANCE_TERMINATE":
        elif action and action.find("TERMINATE") != -1:
          minion_id = minion_info.get_minion_id_by_instance_id(instance_id) 
          #print "minion_id: %s" % minion_id
          if not minion_id:  # did not exist in the minions file - try ec2
            minion_id = ec2.get_private_dns_name(ec2_conn, instance_id)
          item = {'instance_id':str(instance_id), 'minion_id':str(minion_id)}
          minion_info.remove_minion_entry(item)
          key_deleter.delete_key(minion_id)
        sqs.delete_a_message(sqs_conn, queue, message)
  except Exception, e:
    print "\nException!"
    print e
    #log.error("Exception: %s" % e)
    sys.exit(1)


def main(t = SLEEPTIME):
  while True:
    time.sleep(t)
    loop()

if __name__ == "__main__":
  try:
    main()
  except Exception, e:
    log.error("Exception: %s" % e)
    print "Exception: %s" % e

