#!/usr/bin/env python

import salt.client

def it(miniondata="no miniondata passed"):
  f = open("/tmp/testfile.txt",'w')
  f.write( "data.mesasge=" )
  x = str( miniondata['data']['message'] )
  f.write( x )
  f.write("\n")
  f.close()
  return

