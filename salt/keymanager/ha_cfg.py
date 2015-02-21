#!/usr/bin/env python
import yaml

CONFIG_FILE = "/etc/salt/ha/ha-config"


def get_info(config_file=CONFIG_FILE):
  try:
    contents = open(config_file, 'r').read()
    info_dict = yaml.load(contents)
  except Exception, e:
    print "Unable to load config file contents %s" % config_file
    print "Exception: %s" % e
    raise
  return info_dict

def main():
  info = get_info(CONFIG_FILE)
  return info


if __name__ == "__main__":
  print main()
