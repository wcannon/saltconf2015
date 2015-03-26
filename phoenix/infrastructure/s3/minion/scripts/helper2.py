#!/usr/bin/env python
import json
import requests

''' - for reference -
curl http://169.254.169.254/latest/dynamic/instance-identity/document/
{
  "accountId" : "012800249358",
  "instanceId" : "i-f8c10804",
  "billingProducts" : null,
  "imageId" : "ami-9a562df2",
  "instanceType" : "t2.small",
  "kernelId" : null,
  "ramdiskId" : null,
  "pendingTime" : "2015-03-19T14:57:40Z",
  "architecture" : "x86_64",
  "region" : "us-east-1",
  "version" : "2010-08-31",
  "availabilityZone" : "us-east-1a",
  "privateIp" : "10.0.0.72",
  "devpayProductCodes" : null
}
'''

class Helper:
    
    def __init__(self):
        self.METADATA_URL = "http://169.254.169.254/latest/meta-data/"
        self.DYNAMICDATA_URL = "http://169.254.169.254/latest/dynamic/" 

    def get_region(self):
        try:
            r = self.get_dynamic_metadata("region")
        except:
            # log the exception, but return None
            raise
        return r

    def get_zone(self):
        try:
            r = self.get_dynamic_metadata("availabilityZone")
        except:
            # log the exception, but return None
            raise
        return r

    def get_instanceid(self):
        try:
            r = self.get_dynamic_metadata("instanceId")
        except:
            # log the exception, but return None
            raise
        return r

    def get_private_ip(self):
        try:
            r = self.get_dynamic_metadata("privateIp")
        except:
            # log the exception, but return None
            raise
        return r

    def get_dynamic_metadata(self, requested_info):
        '''Returns the dynamic data document as dictionary -- see top of file for reference'''
        result = None
        try:
            url = self.DYNAMICDATA_URL + "instance-identity/document/"
            r = requests.get(url)
            content = r.content
            content_as_dict = json.loads(content)
            result = content_as_dict.get(requested_info, None)
        except:
            raise
        return result

if __name__ == "__main__":
  my_helper = Helper()
  print "Region is: %s" % my_helper.get_region()
  print "Availability Zone is: %s" % my_helper.get_zone()
  print "InstanceId is: %s" % my_helper.get_instanceid()
  print "private ip is: %s" % get_private_ip()
