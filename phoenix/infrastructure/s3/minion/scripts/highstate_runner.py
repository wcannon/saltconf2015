#!/usr/bin/env python
"""Usage: highstate_runner.py MINION_ID

Run a highstate on one minion if it has not been run on the minion previously, and a highstate
is not currently running.  Also, ensure that no other salt masters should run the highstate.

Arguments:
  MINION_ID

Options:
  -h --help

"""
from docopt import docopt
import time
import salt.client
import socket
#import logging

#log = logging.getLogger(__name__)


def check_if_first_highstate_ever(minion_id):
  '''Check if a highstate has ever been run on the minion'''
  # initial highstate creates a file  --> /root/most_recent_salt_highstate_run.txt
  #log.info('FUNCTION: check_if_first_highstate_ever')
  client = salt.client.LocalClient()
  # file.path_exists_glob /root/most_recent_salt_highstate_run.txt
  #mypath = ["/root/most_recent_salt_highstate_run.txt"]
  mypath = ["/etc/salt/highstate_ran_once"]
  results_by_minion = client.cmd(tgt=[minion_id], fun='file.path_exists_glob', arg=mypath, expr_form='list')   # sync call
  #log.info("results_by_minion: %s" % results_by_minion)
  
  if results_by_minion.get(minion_id, False) == False or len(results_by_minion) < 1:
    #log.info("Highstate was not run before")
    return False
  else:
    #log.info("Highstate WAS run before")
    return results_by_minion[minion_id]

def check_if_highstate_running(minion_id):
  '''Check if a highstate is currently running on a minion'''
  #log.info('FUNCTION: check_if_highstate_running')
  client = salt.client.LocalClient()
  #  salt ip-10-0-0-113.ec2.internal saltutil.is_running state.highstate
  running_function = ["state.highstate"]
  results_by_minion = client.cmd(tgt=minion_id, fun='saltutil.is_running', arg=running_function)   # sync call
  minion_results = results_by_minion.get(minion_id, [])
  #log.info("minion_results: %s" % minion_results)
  if not minion_results:
    #log.info("highstate is not currently running")
    return False
  else:
    #log.info("highstate IS currently running")
    return True

def write_highstate_runner_claim(minion_id):
  '''Write our saltmaster's id into a file on the minion, designating which saltmaster gets to run the
     highstate on it.  First in wins.
     /tmp/highstate_runner'''
  client = salt.client.LocalClient()
  path = "/tmp/highstate_runner"
  hostname = socket.gethostname()
  results = client.cmd(tgt=minion_id, fun='file.touch', arg=[path])   # sync call
  results_by_minion = client.cmd(tgt=minion_id, fun='file.append', arg=[path, hostname])   # sync call
  return

def should_run_highstate(minion_id):
  '''Determine if we should run the highstate by checking the first line in /tmp/highstate_runner
     for our hostname'''
  client = salt.client.LocalClient()
  path = "/tmp/highstate_runner"
  hostname = socket.gethostname()
  results_by_minion = client.cmd(tgt=minion_id, fun='cmd.run', arg=["cat /tmp/highstate_runner"])   # sync call
  contents = results_by_minion.get(minion_id, '')
  lines = contents.split("\n")
  first_line = lines[0].strip()
  if first_line == hostname:
    return True
  else:
    return False
# salt ip-10-0-0-113.ec2.internal cmd.run "cat /tmp/highstate_runner"

def call_highstate(minion_id):
  '''execute an async salt call to a minion to run state.highstate asynchronously'''
  client = salt.client.LocalClient()
  minions = client.cmd_async(tgt=minion_id, fun='state.highstate', arg=[], timeout=1, expr_form='compound')
  return 

def write_highstate_ran(minion_id):
  '''Write our saltmaster's id into a file on the minion, designating which saltmaster gets to run the
     highstate on it.  First in wins.
     /tmp/highstate_runner'''
  client = salt.client.LocalClient()
  path = "/etc/salt/highstate_ran_once"
  seconds = time.time()
  results = client.cmd(tgt=minion_id, fun='file.touch', arg=[path])   # sync call
  results_by_minion = client.cmd(tgt=minion_id, fun='file.append', arg=[path, seconds])   # sync call
  return

def main(minion_id):
  '''Wrap all this goodness together coherently'''
  # Return True if this saltmaster runs highstate, False otherwise
  #log.info("Entered main of highstate_runner")
  highstate_already_run =  check_if_first_highstate_ever(minion_id)
  if highstate_already_run:
    print "Highstate run at least once before.  Exiting."
    #log.info("Highstate run at least once before. Exiting")
    return
  highstate_running_now = check_if_highstate_running(minion_id)
  if highstate_running_now:
    print "Highstate is already running.  Exiting."
    ##log.info("Highstate is already running. Exiting")
    return
  # Looks like we might need to run a highstate

  # Attempt to claim the right to run highstate on minion
  print "Attempting to claim the highstate run"
  #log.info("Attempting to claim the highstate run")
  write_highstate_runner_claim(minion_id) 

  winner = should_run_highstate(minion_id)
  if winner:
    print "I'm the winner"
    #log.info("I'm the winner")
    call_highstate(minion_id)
    write_highstate_ran(minion_id)
    return True
  else:   
    print "Another salt master will run highstate.  Exiting."
    #log.inf("Another salt master will run highstate.  Exiting.")
    return False

def manage(miniondata="no miniondata passed"):
  result = False
  #f = open("/tmp/highstate-data", 'w')
  #f.write(str(miniondata))
  #f.write("\n")
  minion_id = miniondata['id']
  act =  miniondata['act']
  if act == 'accept':
    result = main(minion_id)
  return result

if __name__ == '__main__':
  arguments = docopt(__doc__)
  main(arguments['MINION_ID'])
