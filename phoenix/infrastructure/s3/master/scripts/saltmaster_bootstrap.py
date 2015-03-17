#!/usr/bin/env python
import sys
import requests
import subprocess

METADATA_URL = "http://169.254.169.254/latest/meta-data/"
MINION_CONFIG = "/etc/salt/minion"
HA_CONFIG = "/etc/salt/ha/ha_config"

# Note:  a grains file should represent a type of server
commands = [
	  	['add-apt-repository', '-y', 'ppa:saltstack/salt'],
                ['apt-get', 'update'],
                ['apt-get', 'install', '-y', 'salt-minion', 'python-requests', 'salt-cloud',
                 'salt-ssh', 'salt-api', 'salt-doc', 'salt-master'],
                ['mkdir', '-p', '/etc/salt/ha/'],
                ['aws', 's3', 'cp', 's3://BUCKET/minion/minion_config', '/etc/salt/minion'],
                ['aws', 's3', 'cp', 's3://BUCKET/minion/master_list_manager.py', '/usr/bin/'],
                ['aws', 's3', 'cp', 's3://BUCKET/minion/master_list_manager.conf', '/etc/init/'],
                ['aws', 's3', 'cp', 's3://BUCKET/minion/GRAINS_FILE', '/etc/salt/grains'],
                ['service', 'master_list_manager', 'start'],
           ]

def run_command(cmd_as_list):
  '''Take a command as a list of cmd + args and execute it, returning output'''
  result = False
  try:
    #output = subprocess.check_output([/usr/sbin/service", svc_name, "restart"])
    output = subprocess.check_output(cmd_as_list)
  except:
    print "Exception when executing command: %s" % cmd_as_list
    raise
  return

def create_ha_config_file(queue_minion, queue_master, region, bucketname, grainsfile, ha_config=HA_CONFIG):
  '''Populate the ha config file with info passed from the autoscaling group'''
  try:
    f = open(ha_config, 'w')
    f.write("queuename_minion:%s\n" % queue_minion)
    f.write("queuename_master:%s\n" % queue_master)
    f.write("region:%s\n" % region)
    f.write("bucket_name:%s\n" % bucketname)
    f.close()
  except:
    print "Exception when writing salt_ha_config file"
    raise
  return
  

def get_instance_id():
  '''Retrieves instance id from aws meta-data service'''
  content = None
  try:
    url = METADATA_URL + "instance-id"
    r = requests.get(url)
    content = r.content
  except:
    raise
  return content

def run_substitutions(list_of_strs, old, new):
  '''Simple way to replace a string in a list of strings'''
  new_list = []
  for s in list_of_strs:
    t = s.replace(old, new)
    new_list.append(t)
  return new_list
     
def main(queue_minion, queue_master, region, bucketname, grainsfile) 
  output = "place holder" 
  # Run the main set of commands to bootstrap the master
  try:
    for cmd_as_list in commands:
      # simply allowing an easy substitution for the bucket name
      updated_cmd_as_list = run_substitions(cmd_as_list, 'BUCKET', bucket_name)
      updated_cmd_as_list = run_substitions(updated_cmd_as_list, 'GRAINS_FILE', grains_file)
      output = run_command(updated_cmd_as_list)
  except Exception, e:
    print "Error: %s" % output
    print e
    raise

  # retrieve the instance-id from aws
  instanceid = "not-set-properly"
  try:
    instanceid = get_instance_id()
  except Exception, e:
    print "Failed to retrieve instance id"
    raise
  
  # set the minion id to the value of the aws ec2 instance-id
  try:
    f = open(MINION_CONFIG, 'a')
    f.write("id: %s\n" % instanceid)
    f.close()
  except Exception, e:
    print "Failed to set minion id as instance id"
    raise

  # restart the salt-minion service to pick up the changes
  try:
    cmd_as_list = ['service', 'salt-minion', 'restart']
    run_command(cmd_as_list)
  except Exception, e:
    print "Failed to restart salt-minion after setting minion id"
    raise

  # populate the ha-config file
  try:
    create_ha_config_file(queue_minion, queue_master, bucketname, grainsfile)
  except Exception, e:
    print "Failed to create salt ha config file"
    raise

  # Encode the salt master key up / down test in s3
  # Clone our repo locally
  # Copy in master config file
  # Create symlinks
  
    

   
if __name__ == "__main__":
  # expecting parameters
  # p1 = region, p2 = queue_minion, p3 = queue_master, p4 = bucket_name, p5 = grains_file
  region = sys.argv[1]
  queue_minion = sys.argv[2]
  queue_master = sys.argv[3]
  bucket_name = sys.argv[4]
  grains_file = sys.argv[5]
  try:
    main(queue_minion, queue_master, region, bucketname, grainsfile) 
  except Exception, e:
    print "Error! %s" % e
