#!/usr/bin/env python
import boto
import boto.dynamodb
from boto.dynamodb2.fields import HashKey
from boto.dynamodb2.table import Table

def connect(region='us-east-1'):
  conn = False
  try:
    conn = boto.dynamodb.connect_to_region(region)
  except:
    raise
  return conn

def list_tables():
  tables = []
  try:
    conn = connect()
    tables = conn.list_tables()
  except Exception, e:
    raise e
  return tables

def create_table(tablename):
  # Need to wait for table status to be ready before using
  existing_tables = list_tables()
  if tablename not in existing_tables:
    try:
      newtable = Table.create(tablename, schema=[HashKey('instanceid')])
    except Exception, e:
      raise e
  else:
    newtable = False
  return newtable

def add_minion(instanceid):
  result = False
  try:
    minions = Table('minions')
    result = minions.put_item(data={'instanceid':instanceid})
  except Exception, e:
    raise e
  return result
    
def get_minion(instanceid):
  result = False
  try:
    minions = Table('minions')
    result = minions.get_item(instanceid=instanceid)
  except Exception, e:
    raise e
  return result

if __name__ == "__main__":
  minions = False
  try:
    mytable = create_table('minions')
    if mytable:
      print "Table description: %s" % mytable.describe()
    else:
      print "Table 'minions' already exists"
  except Exception, e:
    print "Exception occurred creating minions table"
    print e

  try:
    mytable = create_table('masters')
    if mytable:
      print "Table description: %s" % mytable.describe()
    else:
      print "Table 'masters' already exists"
  except Exception, e:
    print "Exception occurred creating masters table"
    print e

  try:
    print "\nTables already created are: %s" % list_tables()
  except Exception, e:
    print e

  try:
    m = False
    print "\Adding a minion to minions table"
    m = add_minion('i-123456')
  except Exception, e:
    print e
  print "m = %s" % m

  try:
    m = False
    print "\Getting a minion from the minions table"
    m = get_minion('i-123456')
  except Exception, e:
    print e
  print "m = %s" % m.__dict__
