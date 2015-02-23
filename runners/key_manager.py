#!/usr/bin/env python
import sys
import salt
import yaml
import salt.client
from salt.key import Key


opts = salt.config.master_config('/etc/salt/master')
mymanager = Key(opts)
#aws_minion_file = "/etc/salt/ha/aws-autoscaling-info/aws_minion_info.yaml"
aws_minion_file = "/etc/salt/ha/aws-autoscaling-info/aws_minions.yaml"

'''  Reference of yaml on aws_minion_file - a list of dictionaries
 -  { 'minion_id': 'ip-10-0-10-137.ec2.internal', 'instance_id': 'i-4e087261'}
 -  { 'minion_id': 'ip-10-0-10-137.ec2.internal', 'instance_id': 'i-4e087261'}
'''

def load_minion_info(file_path=aws_minion_file):
  mydict = [] # useful if sns/sqs have not provided any info = no minion file yet
  mystr = "no data"
  try:
    #mydict = yaml.load(open(file_path, "r").read())
    minions = yaml.load(open(file_path, "r").read())
    #minions = mydict.get('minions', [])
  except Exception, e:
    print "Unable to open file, or convert to dict, giving an empty dict"
    print "Exception: %s" % e
    print "mystr = %s" % mystr
    print "mydict %s" % mydict
    raise
  return minions

def get_minion_expected(minion_list, minion_id):
  result = False
  for m in minion_list:
    if m.get('minion_id', 'nobody') == minion_id:
      result = True
      break
  return result
 
def manage(miniondata="no miniondata passed"):
  minion_id = str( miniondata.get('id', 'nobody') )
  minion_list = load_minion_info(aws_minion_file)
  result = get_minion_expected(minion_list, minion_id)

  if result: 
    try:
      accept_key(minion_id)
    except Exception, e:
      raise
  return

def accept_key(minion_id):
  mymanager = Key(opts)
  mymanager.accept(match=minion_id)
  return


if __name__ == "__main__":

  minion_id = None
  if len(sys.argv) > 1:
   minion_id = sys.argv[1]
  
  #print "\nList of all accepted keys:"
  #minions = get_current_minions()
  #print (", ").join(minions) 

  # example accept
  if minion_id:
    test_manage(minion_id)

  # example delete
  #if minion_id:
  #  delete_key(minion_id)


  print "\nList of all accepted keys:"
  minions = get_current_minions()
  print (", ").join(minions) 
