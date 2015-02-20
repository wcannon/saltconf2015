#!/usr/bin/env python
import boto
import boto.sqs
import boto.vpc

conn = boto.sqs.connect_to_region("us-east-1")

print "available queues:"
for q in conn.get_all_queues():
  print q

myq = conn.get_queue('sm1')
print "myq: "
print myq

rs = myq.get_messages()
print "length of rs: %s" % len(rs)

print "first message info"
print
print rs[0].get_body()

'''
Connect to designated queue.
Grab messages and process them, one at a time, removing a message from the queue after
processing completes.
process = download + determine purpose (new key, delete key) + lookup private ip of instance id
          + translate to expected minion id + append to end of "db file"
'''

def get_message(sqs_connection, queue_name):
    pass

def determine_instance_id(message):
    pass

def lookup_internal_ip(vpc_connection, instance_id):
    pass

def create_expected_minion_id(internal_ip):
    pass

def get_time_in_secods_since_epoch():
    pass

def append_to_db_file(filename, minion_id, key_action, epoch_seconds):
    pass

def delete_key_on_local_master(minion_id):
    '''If key not already deleted on local master, delete it'''
    pass

def accept_key_on_local_master(minion_id):
    '''If key not already accepted on local master and no more than 15 minutes
       have passed since receiving the autoscaling notification, accept it'''
    pass










