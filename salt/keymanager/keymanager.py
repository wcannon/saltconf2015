#!/usr/bin/env python
import boto
import boto.sqs

conn = boto.sqs.connect_to_region("us-east-1")

print "available queues:"
for q in conn.get_all_queues():
  print q

