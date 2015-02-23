#!/usr/bin/env python
import yaml
import requests

CONFIG_FILE = "/etc/salt/ha/ha-config"
METADATA_URL = "http://169.254.169.254/latest/meta-data/"


def get_info(config_file=CONFIG_FILE):
  try:
    contents = open(config_file, 'r').read()
    info_dict = yaml.load(contents)
  except Exception, e:
    print "Unable to load config file contents %s" % config_file
    print "Exception: %s" % e
    raise
  return info_dict

def get_ec2_dns():
  content = None
  try:
    url = METADATA_URL + "public-hostname"
    r = requests.get(url)
    content = r.content
  except:
    raise
  return content

# previous bash calls
#instancedns=`curl -s http://169.254.169.254/latest/meta-data/public-hostname`
#sed  "s/new-dns-name/$dnsname/" /tmp/rrset_template.json | sed "s/target-dns-name/$instancedns/" > /tmp/rrset2.json
#aws --region us-east-1 route53 change-resource-record-sets --hosted-zone-id Z2IBYTQ6W9V2HA --change-batch file:///tmp/rrset2.json

rrset_template='''{
  "Comment": "Create or Update a dns cname record for a salt-master",
  "Changes": [
    {
      "Action": "UPSERT",
      "ResourceRecordSet": {
        "Name": "my-saltmaster-dns-name",
        "Type": "CNAME",
        "TTL": 60,
        "ResourceRecords": [
          {
            "Value": "aws-target-dns-name"
          }
        ]
      }
    }
  ]
}'''

if __name__ == "__main__":
  info_dict = get_info()
  region = info_dict.get('region', None)
  print "Region: %s" % region
  sm_dns_name = info_dict.get('dns_name', None)
  print "SaltMaster DNS Name: %s" % sm_dns_name
  aws_dns_name = get_ec2_dns()
  print "AWS EC2 DNS Name: %s" % aws_dns_name
  print
  print
  str2 = rrset_template.replace("my-saltmaster-dns-name", sm_dns_name)
  str3 = str2.replace("aws-target-dns-name", aws_dns_name)
  print "rrset.json is now:"
  print str3
