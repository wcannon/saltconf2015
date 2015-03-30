#!/usr/bin/env python
import sys
import salt
import salt.client
from key_manager import KeyManager
from instance_manager import MinionManager
from helper import Helper

# minion id = aws instance_id

def accept_minion_key(minion_id):
    try:
        k = KeyManager()
        k.accept_key(minion_id)
    except:
        raise
    return

def main(miniondata):
    try:
        minion_id = str( miniondata.get('id', 'nobody') )
        h = Helper()
        region = h.get_region()
        mm = MinionManager(region)
        expected_minion_id_list = mm.get_launched()
        if minion_id in expected_minion_id_list:
            accept_minion_key(minion_id) 
    except:
        raise

if __name__ == "__main__":

    minion_id = None
    if len(sys.argv) > 1:
        minion_id = sys.argv[1]
        main({'id':minion_id})
