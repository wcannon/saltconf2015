#!/usr/bin/env python
import sys
import salt
import logging
from salt.key import Key


log = logging.getLogger(__name__)

opts = salt.config.master_config('/etc/salt/master')
mymanager = Key(opts)

def delete_key(minion_id):
  mymanager = Key(opts)
  mymanager.delete_key(minion_id)
  return

if __name__ == "__main__":
  try:
    minion_id = sys.argv[1]
    delete_key(minion_id)
  except Exception, e:
    print "Error!"
    print e
  
