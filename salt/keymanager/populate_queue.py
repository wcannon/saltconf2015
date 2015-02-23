#!/usr/bin/env python
import boto.sqs
import boto.sqs.message

region = 'us-east-1'
queue = 'sm1'


msg1 = open("instance_launch_msg.txt", "r").read()
msg2 = open("instance_termination_msg.txt", "r").read()
msg3 = open("instance_launch_msg1.txt", "r").read()
msg4 = open("instance_launch_msg2.txt", "r").read()

conn = boto.sqs.connect_to_region(region)
myq = conn.get_queue(queue)
my_messages = [msg1,msg4,msg3,msg2]
for msg in my_messages:
  m =  boto.sqs.message.Message()
  m.set_body(msg)
  myq.write(m)

