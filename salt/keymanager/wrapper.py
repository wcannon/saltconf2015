#!/usr/bin/env python
import sys
import sqs
import msg
import time

if __name__ == "__main__":
  try:
    region = open("/root/region").read().strip()
    print "region: %s" % region
    queue_name = open("/root/queuename").read().strip()
    print "queue_name: %s" % queue_name
  except:
    print "Files expected: /root/region, /root/queuename"
    print "Unable to open region or queuname file, exiting."
    sys.exit(1)

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

  

