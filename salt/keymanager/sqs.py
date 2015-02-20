#!/usr/bin/env python
import sys
import boto.sqs

def get_queue_length(conn, queue):
  try:
    myq = conn.get_queue('sm1')
  except:
    raise
  return  myq.count()
  
def get_a_message(conn, queue):
  try:
    myq = conn.get_queue('sm1')
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
    myq = conn.get_queue('sm1')
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


if __name__ == "__main__":
  # e.g. ./msg.py us-east-1 sm1
  region = sys.argv[1]
  queue_name = sys.argv[2]
  try:
    main(region, queue_name)
  except:
    print "Error in sqs message retrieval"
    raise


