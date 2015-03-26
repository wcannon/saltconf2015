#!/usr/bin/env python
import json
import yaml
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
        self.METADATA_URL =    "http://169.254.169.254/latest/meta-data/"
        self.DYNAMICDATA_URL = "http://169.254.169.254/latest/dynamic/" 
        self.AWS_HA_CONFIG_FILE = "/etc/salt/ha/ha-config"
        self.ha_info_dict = self.load_ha_config_info() # loads region, queuename_master, queuename_minion and etc

    def load_ha_config_info(self, file_path=None):
        '''This provides access to info such as region, queue_name for connecting to sqs and ec2'''
        try:
            if not file_path:
                file_path=self.AWS_HA_CONFIG_FILE
            mydict = yaml.load(open(file_path, "r").read())
        except Exception, e:
            # log the exception, but return None
            raise
        return mydict
 
    def get_minion_queue_name(self):
        try:
            queue_name = self.ha_info.get("queuename_minion", None)
        except:
            # log the exception, but return None
            raise
        return queue_name

    def get_master_queue_name(self):
        try:
            queue_name = self.ha_info.get("queuename_master", None)
        except:
            # log the exception, but return None
            raise
        return queue_name

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
  print "private ip is: %s" % my_helper.get_private_ip()
  print "ha-info %s" % my_helper.ha_info_dict
