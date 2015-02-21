#!/usr/bin/env python

import salt.client

def manage(miniondata="no miniondata passed"):
  f = open("/tmp/key_manager.txt",'w')
  f.write( "data.mesasge=" )
  x = str( miniondata['data']['message'] )
  f.write( x )
  f.write("\n")
  f.close()
  return

