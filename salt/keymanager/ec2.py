#!/usr/bin/env python
import sys
import boto.vpc

# e.g. myinstances = conn.get_only_instances(instance_ids=['i-9d2fa972']) --> returns a reservation
# myinstances[0].instances[0].private_ip_address ---> gives the private ip address 
# myinstances[0].instances[0].private_dns_name  ---> gives the minion id!

def get_private_dns_name(conn, instance_id):
  myinstances = conn.get_only_instances(instance_ids=[instance_id])
  return myinstances[0].private_dns_name
  #return myinstances[0].instances[0].private_dns_name 
  

if __name__ == "__main__":
  instance_id = sys.argv[1]
  region = 'us-east-1'
  conn = boto.vpc.connect_to_region(region)
  minion_id =  get_private_dns_name(conn, instance_id)
  print "minion id is %s" % minion_id
