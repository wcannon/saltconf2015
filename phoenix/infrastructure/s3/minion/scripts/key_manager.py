#!/usr/bin/env python
import sys
import salt
import salt.config
from salt.key import Key

class KeyManager:                                                                                                    
    def __init__(self):                                                                                              
        self.opts = salt.config.master_config('/etc/salt/master')
        self.mykeymgr = Key(self.opts)

    def get_minion_keys(self, status=None):
        '''Return a list of minion keys matching status type'''
        #  Key.list_status(status)  where status type = accepted, pre, rejected, all
        #  or, use Key.list_keys(self)  --> dict of minions_rejected, minions_pre, minions
        if status not in ['pre', 'accepted', 'rejected']:
            result = None
        else:
            try:
                r_dict = self.mykeymgr.list_status(status)
                k = r_dict.keys()
                result = r_dict.get(k[0], None)
            except Exception, e:
                raise
        return result
        

    def reject_key(self, key):
        '''Reject a key, if it exists'''
        pass

    def reject_keys(self, key_list):
        '''Reject each key in list,  if it exists'''
        # Key.reject(self, match, match_dict, include_accepted)
        pass

    def delete_key(self, key):
        '''Delete a key, if it exists'''
        try:
            self.mykeymgr.delete_key(key)
        except Exception, e:
            pass
        return 

    def delete_keys(self, key_list):
        '''Delete each key in list, if it exists'''
        if key_list:
            for key in key_list:
                try:
                    self.delete_key(key)
                except Exception, e:
                    raise
        return

    def accept_key(self, key):
        '''Accept a key, if it exists'''
        pass

    def accept_keys(self, key_list):
        '''Accept each key in list, if it exists'''
        pass


if __name__ == "__main__":
    k = KeyManager()
    print k.get_minion_keys(status='pre')
    print k.get_minion_keys(status='not-valid')
    
