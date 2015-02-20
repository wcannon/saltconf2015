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
import salt.client


def check_if_first_highstate(minion_id):
  '''Check if a highstate has ever been run on the minoin'''
  client = salt.client.LocalClient()
  client.cmd()   # sync call
  pass

def check_if_highstate_running(minion_id):
  '''Check if a highstate is currently running on a minion'''
  client = salt.client.LocalClient()
  client.cmd()   # sync call
  pass

def write_highstate_runner_id(minion_id):
  '''Write our saltmaster's id into a file on the minion, designating which saltmaster gets to run the
     highstate on it.  First in wins.
     /tmp/highstate_runner'''
  client = salt.client.LocalClient()
  client.cmd()   # sync call
  pass

def call_highstate(minion_id):
  '''execute an async salt call to a minion to run state.highstate asynchronously'''
  client = salt.client.LocalClient()
  minions = client.cmd_async(tgt=minion_id, fun=state.highstate, arg=[], timeout=1, expr_form='compound')
  return 

if __name__ == '__main__':
  arguments = docopt(__doc__)
  print(arguments)
  minion_id = arguments['MINION_ID']
  print "minion_id: %s" % minion_id

  # has highstate ever been run before?

  # is there a file (/tmp/highstate_runner) with my hostname in  it?

  # is a highstate already running?

  # run a highstate

