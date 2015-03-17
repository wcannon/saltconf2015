#!/usr/bin/env python
import yaml
import requests
import boto.route53
from boto.route53.record import ResourceRecordSets


CONFIG_FILE = "/etc/salt/ha/ha-config"
METADATA_URL = "http://169.254.169.254/latest/meta-data/"


def get_info(config_file=CONFIG_FILE):
  #instancedns=`curl -s http://169.254.169.254/latest/meta-data/public-hostname`
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

def update_template(template_string, sm_dns_name, aws_dns_name):
  str2 = rrset_template.replace("my-saltmaster-dns-name", sm_dns_name)
  str3 = str2.replace("aws-target-dns-name", aws_dns_name)
  newstr1 = template_string.replace("my-saltmaster-dns-name", sm_dns_name)
  newstr2 = newstr1.replace("aws-target-dns-name", aws_dns_name)
  return newstr2
  
# previous bash calls
#sed  "s/new-dns-name/$dnsname/" /tmp/rrset_template.json | sed "s/target-dns-name/$instancedns/" > /tmp/rrset2.json
#aws --region us-east-1 route53 change-resource-record-sets --hosted-zone-id Z2IBYTQ6W9V2HA --change-batch file:///tmp/rrset2.json
#aws --region us-east-1 route53 change-resource-record-sets --hosted-zone-id Z2IBYTQ6W9V2HA --change-batch  '{}'

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

def get_route53_connection(region):
  conn = None
  try:
    conn = boto.route53.connect_to_region(region)
  except Exception, e:
    print "Exception: %s" % e
  return conn
 
def update_dns_cname_record(conn, zone_id, cname_record, cname_value):
  # zone_id = 'Z2IBYTQ6W9V2HA'
  # cname_record = 'sol1-salt1.devopslogic.com'
  result = None
  try:
    changes = ResourceRecordSets(conn, zone_id)
    change = changes.add_change("UPSERT", cname_record, "CNAME", 60)
    change.add_value(cname_value)
    result = changes.commit()
  except Exception, e:
    print "Exception: %s" % e
  return result

if __name__ == "__main__":
  info_dict = get_info()
  region = info_dict.get('region', None)
  print "Region: %s" % region
  sm_dns_name = info_dict.get('dns_name', None)
  print "SaltMaster DNS Name: %s" % sm_dns_name
  aws_dns_name = get_ec2_dns()
  print "AWS EC2 DNS Name: %s" % aws_dns_name
  hosted_zone_id = info_dict.get('hosted_zone_id', None)
  print "Hosted Zone ID: %s" % hosted_zone_id
  print
  conn = get_route53_connection(region)
  result = update_dns_cname_record(conn, hosted_zone_id, sm_dns_name, aws_dns_name)
  print result
