#!/usr/bin/env python
import sys
import json

def get_instance_action(message):
    '''Determines action type (launch / terminate), and returns action type and aws instance-id'''
    mydict = json.loads(message)
    messagebody = mydict['Message']
    bodydict = json.loads(messagebody)
    return bodydict['EC2InstanceId']

def get_instance_id(message):
    '''Returns the aws instance id'''
    mydict = json.loads(message)
    messagebody = mydict['Message']
    bodydict = json.loads(messagebody)
    return bodydict['Event']


if __name__ == "__main__":
  filename = sys.argv[1]
  f = open(filename, "r")
  message = f.read()
  print "instance action: %s" % get_instance_action(message)
  print "instance id: %s" % get_instance_id(message)
