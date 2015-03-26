#!/usr/bin/env python
import sys
import salt
from salt.key import Key

class KeyDeleter:
    
    def __init__(self):
        self.opts = salt.config.master_config('/etc/salt/master')
        self.mymanager = Key(opts)

    def delete_key(self, minion_id):
        '''This provides a convenient way to delete a key from Salt'''
        try:
            self.mymanager.delete_key(minion_id)
        except Exception, e:
            # log the exception, but return None
            raise
        return 


if __name__ == "__main__":
  try:
    minion_id = sys.argv[1]
    my_deleter = KeyDeleter()
    my_deleter.delete_key(minion_id)
  except Exception, e:
    print "An exception was raised: %s" % e
  
