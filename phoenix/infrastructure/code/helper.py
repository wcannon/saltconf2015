#!/usr/bin/env python
import json
import requests

METADATA_URL = "http://169.254.169.254/latest/meta-data/"
DYNAMICDATA_URL = "http://169.254.169.254/latest/dynamic/" 
'''
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

def get_region():
  r = None
  try:
    dyn_info = json.loads(get_dynamic_metadata("instance-identity/document/"))
    r = dyn_info.get("region", "None")
  except:
    pass
  return r

def get_zone():
  r = None
  try:
    dyn_info = json.loads(get_dynamic_metadata("instance-identity/document/"))
    r = dyn_info.get("availabilityZone", "None")
  except:
    pass
  return r

def get_instanceid():
  r = None
  try:
    dyn_info = json.loads(get_dynamic_metadata("instance-identity/document/"))
    r = dyn_info.get("instanceId", "None")
  except:
    pass
  return r

def get_private_ip():
  r = None
  try:
    dyn_info = json.loads(get_dynamic_metadata("instance-identity/document/"))
    r = dyn_info.get("privateIp", "None")
  except:
    pass
  return r

def get_dynamic_metadata(info):
  content = None
  try:
    url = DYNAMICDATA_URL + info
    r = requests.get(url)
    content = r.content
  except:
    raise
  return content

if __name__ == "__main__":
  print "region is: %s" % get_region()
  print "zone is: %s" % get_zone()
  print "instanceId is: %s" % get_instanceid()
  print "private ip is: %s" % get_private_ip()
