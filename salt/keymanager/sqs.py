#!/usr/bin/env python
import sys
import boto.sqs

def get_all(queues):
  return conn.get_all_queues()

def get_queue_length(conn, queue):
  myq = conn.get_queue('sm1')
  return  myq.count()
  
def get_a_message(conn, queue):
  myq = conn.get_queue('sm1')
  message = myq.read()
  return message

def print_message(message):
  print message.get_body()
  return

def delete_a_message(queue, message):
  myq.delete_message(message)
  return 

if __name__ == "__main__":
  region = sys.argv[1]
  queue = sys.argv[2]
  conn = boto.sqs.connect_to_region(region)
  message1 = get_a_message(conn, queue)
  print message1
  #print "queue length: %s" % get_queue_length(conn, queue)
  #delete_a_message(conn, queue)
  #print "queue length is now: %s" % get_queue_length(conn, queue)

