#!/usr/bin/env python
import subprocess

def get_service_running(svc_name):
  result = False
  try:
    output = subprocess.check_output(["service", svc_name, "status"])
    if "running" in output:
      result = True
    else:
      result = False
  except:
    print "Exception when checking service [%s] status" % svc_name
    raise
  return result

def start_service(svc_name):
  result = False
  try:
    output = subprocess.check_output(["service", svc_name, "start"])
    if "running" in output:
      result = True
    else:
      result = False
  except:
    print "Exception when starting service [%s] status" % svc_name
    raise


if __name__ == "__main__":
  service = "salt-minion"
  is_running = get_service_running(service)
  if not is_running:
    print "Starting service [%s]" % service
    try:
      start_service(service)
    except Exception, e:
      print "Error thrown when starting [%s]" % service
      print e

