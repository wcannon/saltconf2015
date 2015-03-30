#!/usr/bin/env python
import os
import sys
import requests
import subprocess

METADATA_URL = "http://169.254.169.254/latest/meta-data/"
MINION_CONFIG = "/etc/salt/minion"
CONFIG_DIR = "/etc/salt/ha"

# Note:  a grains file should represent a type of server
commands = [
                ['add-apt-repository', '-y', 'ppa:saltstack/salt'],
                ['apt-get', 'update'],
                ['apt-get', 'install', '-y', 'salt-minion', 'python-requests', 'python-pip'],
                ['aws', 's3', 'cp', 's3://BUCKET/minion/config/minion_config', '/etc/salt/minion'],
                ['pip', 'install', '--upgrade', 'dynamodb-mapper'],
                ['mkdir', '-p', '/usr/local/bin/phoenix'],
                ['aws', 's3', 'cp', 's3://BUCKET/minion/scripts/master_list_manager.py', '/usr/local/bin/phoenix'],
                ['aws', 's3', 'cp', 's3://BUCKET/minion/scripts/helper.py', '/usr/local/bin/phoenix'],
                ['aws', 's3', 'cp', 's3://BUCKET/minion/scripts/instance_manager.py', '/usr/local/bin/phoenix'],
                ['aws', 's3', 'cp', 's3://BUCKET/minion/scripts/ddb.py', '/usr/local/bin/phoenix'],
                ['aws', 's3', 'cp', 's3://BUCKET/minion/scripts/msg.py', '/usr/local/bin/phoenix'],
                ['aws', 's3', 'cp', 's3://BUCKET/minion/scripts/sqs.py', '/usr/local/bin/phoenix'],
                ['aws', 's3', 'cp', 's3://BUCKET/minion/scripts/key_manager.py', '/usr/local/bin/phoenix'],
                ['aws', 's3', 'cp', 's3://BUCKET/minion/scripts/master_list_manager.conf', '/etc/init/'],
                ['aws', 's3', 'cp', 's3://BUCKET/minion/grains_files/GRAINS_FILE', '/etc/salt/grains'],
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
    
def write_config_file(bucket, masters_table):
  '''Write a file that can be referenced by other scripts during ec2 instance lifetime'''
  config_dir = CONFIG_DIR
  mydict = {'bucket': bucket, 'masters_table': masters_table}
  try:
    if not os.path.exists(config_dir):
        os.makedirs(config_dir)
    my_file_path = config_dir + os.sep + "ha-config"
    if not os.path.exists(my_file_path):  # means we're not on a salt-master, create our file
        f = open(config_dir + os.sep + "ha-config", "a")
        for k,v in mydict.items():
          f.write(k + ":" + v + "\n")
        f.close()
  except:
    raise
  return
  
def main(bucket_name, grains_file, masters_table):
  output = "place holder" 
  # Run the main set of commands to bootstrap the minion 
  try:
    write_config_file(bucket_name, masters_table)
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
  bucket_name = sys.argv[1]
  grains_file = sys.argv[2]
  masters_table = sys.argv[3]
  try:
    main(bucket_name, grains_file, masters_table) 
  except Exception, e:
    print "Error! %s" % e
