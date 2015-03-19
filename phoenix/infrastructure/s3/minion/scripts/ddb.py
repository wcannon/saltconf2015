#!/usr/bin/env python
from datetime import datetime
from dynamodb_mapper.model import DynamoDBModel, utc_tz, ConnectionBorg

#http://dynamodb-mapper.readthedocs.org/en/latest/api/model.html#data-models
def set_region(region_name):
  try:
    cbi = ConnectionBorg()
    cbi.set_region(region_name)
  except Exception, e:
    print "Problem changing regions for dynamodb connection"
    raise
  return

class MinionInstance(DynamoDBModel):
  __table__ = u"minions"
  __hash_key__ = u"instanceid"
  __schema__ = {
    u"instanceid": unicode,
    u"modified": datetime,
    u"highstate_ran": bool,
    u"highstate_runner": unicode,
    u"status": unicode,
    }

  __defaults__ = {
     u"modified": lambda: datetime.now(utc_tz),
     u"highstate_ran": False,
     u"highstate_runner": None,
     u"status": u"active",
     }

class MasterInstance(DynamoDBModel):
  __table__ = u"masters"
  __hash_key__ = u"instanceid"
  __schema__ = {
    u"instanceid": unicode,
    u"modified": datetime,
    u"active": bool,
    u"ipaddr": unicode,
    }

  __defaults__ = {
     u"modified": lambda: datetime.now(utc_tz),
     u"active": False,
     u"ipaddr": None,
     }
