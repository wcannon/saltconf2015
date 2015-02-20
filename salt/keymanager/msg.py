#!/usr/bin/env python
import sys
import json

def get_instance_action(message):
    '''Determines action type (launch / terminate), and returns action type and aws instance-id'''
    mydict = json.loads(message)
    return mydict

if __name__ == "__main__":
  filename = sys.argv[1]
  f = open(filename, "r")
  message = f.read()
  mydict = get_instance_action(message)
  #for k in mydict.keys():
  #  print k, mydict[k] 
  #print mydict['Subject']
  messagebody = mydict['Message']
  bodydict = json.loads(messagebody)
  print "instance id: %s" % bodydict['EC2InstanceId']
  print "action: %s" % bodydict['Event']
