#!/usr/bin/env python
import sys
import json


class Msg:
    
    def __init__(self, message):
        if message:
            self.message = message

    def get_body(self, message):
        try:
            bodydict = {}
            #text = message.get_body()
            mydict = json.loads(message)
            messagebody = mydict['Message']
            bodydict = json.loads(messagebody)
        except Exception, e:
            # log.error("Error: %s" % e)
            print e
        #return bodydict.get('Event', None)
        return bodydict
    
    def get_instance_id(self):
        try:
            text = self.get_body(self.message)
        except Exception, e:
            # log.error("Error: %s" % e)
            print e
        return text.get('EC2InstanceId', None)

    def get_instance_action(self):
        try:
            bodydict = {}
            actual_event = None
            text = self.get_body(self.message)
            event = text.get('Event', None)
            # example string being split --> autoscaling:EC2_INSTANCE_LAUNCH
            if event == "autoscaling:EC2_INSTANCE_LAUNCH":
                result = "LAUNCH"
            elif event == "autoscaling:EC2_INSTANCE_TERMINATE":
                result = "TERMINATE"
            else:
                result = None
        except Exception, e:
            # log.error("Error: %s" % e)
            pass
        return result

if __name__ == "__main__":
  message = None
  try:
      filename = sys.argv[1]
      f = open(filename, "r")
      message = f.read()
  except Exception, e:
      print "Unable to read message input file: %s" % e

  try:
      m = Msg(message)
      print "instance id: %s" % m.get_instance_id()
      print "instance action: %s" % m.get_instance_action()
  except Exception, e:
      print "Unable to retrieve data from message: %s" % e
