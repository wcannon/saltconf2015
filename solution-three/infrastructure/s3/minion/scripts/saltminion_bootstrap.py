#!/usr/bin/env python
import sys
import requests
import subprocess

METADATA_URL = "http://169.254.169.254/latest/meta-data/"
MINION_CONFIG = "/etc/salt/minion"

# Note:  a grains file should represent a type of server
commands = [
	  	['add-apt-repository', '-y', 'ppa:saltstack/salt'],
                ['apt-get', 'update'],
                ['apt-get', 'install', '-y', 'salt-minion', 'python-requests'],
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
     
def main(bucket_name, grains_file):
  output = "place holder" 
  # Run the main set of commands to bootstrap the minion 
  try:
    for cmd_as_list in commands:
      # simply allowing an easy substitution for the bucket name
      updated_cmd_as_list = run_substitutions(cmd_as_list, 'BUCKET', bucket_name)
      updated_cmd_as_list = run_substitutions(updated_cmd_as_list, 'GRAINS_FILE', grains_file)
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

   
if __name__ == "__main__":
  # expecting two parameters
  # p1 = bucket name, p2 = filename of grains file 
  bucket_name = sys.argv[1]
  grains_file = sys.argv[2]
  try:
    main(bucket_name, grains_file) 
  except Exception, e:
    print "Error! %s" % e
