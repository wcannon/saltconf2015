#!/usr/bin/env python

import salt.client

def it(data):
  f = open("/tmp/testfile.txt",'w')
  f.write("Wow....this worked!\n")
  f.write(data)
  f.write("\n")
  f.close()
  return

