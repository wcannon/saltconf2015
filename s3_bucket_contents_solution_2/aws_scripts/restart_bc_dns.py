#!/usr/bin/env python
import yaml
import socket
import subprocess

MASTER_FILE = "/etc/salt/minion"
DNS_IP_FILE = "/etc/salt/dns_ip_file"

def get_masters(master_file=MASTER_FILE):
  try:
    f = open(master_file,'r')
    mystr = f.read()
    mydict = yaml.load(mystr)
    masters = mydict.get('master', 'unable-to-find-master-line')
  except:
    raise
  return masters

def lookup_ip(dns_name):
  try:
    ipaddr = socket.gethostbyname(dns_name)
  except:
    raise
  return ipaddr

def lookup_previous_ip_addrs(dns_ip_file=DNS_IP_FILE):
  previous = False
  try:
    f = open(dns_ip_file, 'r')
    previous = f.readlines() 
  except Exception, e:
    print "File not found - should create it"
  return previous

def write_ip_addrs(ip_addrs_list, dns_ip_file=DNS_IP_FILE):
  f = open(dns_ip_file, 'w')
  for ip in ip_addrs_list:
    f.write(ip)
    f.write("\n")
  f.close()
  return

def restart_service(svc_name):
  result = False
  try:
    output = subprocess.check_output(["/usr/sbin/service", svc_name, "restart"])
    print "restarting service - %s" % svc_name
  except:
    print "Exception when restarting service [%s] status" % svc_name
    raise
  return

def main():
  try:
    result = lookup_previous_ip_addrs()
    masters = get_masters() 
    ip_addrs = []
    if not result:  # no previous ip file exists, create one
      for m in masters:
        ip = lookup_ip(m)
        ip_addrs.append(ip)
      write_ip_addrs(ip_addrs, DNS_IP_FILE)
    else:
      # Get the actual dns -> ip results current
      for m in masters:
        ip = lookup_ip(m)
        ip_addrs.append(ip)
      # Get the previous dns-> ip results
      #print "ip_addrs: %s" % ip_addrs
      previous_ip_addrs = lookup_previous_ip_addrs()
      #print "previous ip addrs: %s" % previous_ip_addrs
      for pip in previous_ip_addrs:
        pip = pip.strip("\n")
        if pip not in ip_addrs:
          write_ip_addrs(ip_addrs, DNS_IP_FILE)
          restart_service('salt-minion')
          break
  except:
    raise
  return 

if __name__ == "__main__":
  try:
    main()
  except Exception, e:
    print "Something broke..%s" % e
