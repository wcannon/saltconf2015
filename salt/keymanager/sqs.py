#!/usr/bin/env python
import boto.sqs
import sqs
import yaml
import salt
import logging

log = logging.getLogger(__name__)
opts = salt.config.master_config('/etc/salt/master')
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

def get_queue_length(conn, queue):
  try:
    myq = conn.get_queue(queue)
  except:
    raise
  return  myq.count()
  
def get_a_message(conn, queue):
  '''If we have at least one message in the queue, return it.
     Otherwise, return None''' 
  message = None
  try:
    myq = conn.get_queue(queue)
    q_length = myq.count()
    if q_length > 0:
      message = myq.read()
  except:
    raise
  return message

def print_message(message):
  try:
    print message.get_body()
  except:
    raise
  return

def delete_a_message(conn, queue, message):
  try:
    myq = conn.get_queue(queue)
    myq.delete_message(message)
  except:
    raise
  return 

def main(region, queue_name):
  '''Retrieve all messages from a specified queue, and return them as a list'''
  message_list = []
  try:
    conn = boto.sqs.connect_to_region(region)
    num_messages = get_queue_length(conn, queue_name)
    if num_messages > 0:
      while num_messages > 0:
        message = get_a_message(conn, queue_name)
        message_list.append(message)
        delete_a_message(conn, queue_name, message)
        num_messages -= 1
  except Exception, e:
    print "Exception: %s" % e
    raise
  return message_list    


def get_connection(region):
  conn = None
  try:
    conn = boto.sqs.connect_to_region(region)
  except Exception, e:
    log.error("Unable to connect to aws sqs")
    raise 
  return conn

if __name__ == "__main__":
  info = load_ha_config_info()
  region = info['region']
  queue = info['queue_name']
  conn = boto.sqs.connect_to_region(region)
  print "info: %s" % info
  print
  print "Retrieving a message:"
  msg = get_a_message(conn, queue)
  if msg:
    print_message(msg)
    delete_a_message(conn, queue, msg)
  else:
    print "No messages left to process"
