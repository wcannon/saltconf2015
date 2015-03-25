#!/usr/bin/env python
import boto.sqs
import boto.sqs.message

region = 'us-east-1'
#queue = 'SqsMinion'
queue = 'SqsMaster'


msg1 = open("instance_launch_msg.txt", "r").read()
msg2 = open("instance_launch_msg2.txt", "r").read()

conn = boto.sqs.connect_to_region(region)
print "conn = %s" % conn
myq = conn.get_queue(queue)
print "myq = %s" % myq
my_messages = [msg1,msg2]
for m in my_messages:
  mymessage =  boto.sqs.message.Message()
  mymessage.set_body(m)
  myq.write(mymessage)

