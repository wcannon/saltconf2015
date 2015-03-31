#!/usr/bin/env python
import sys
import yaml
import time
import subprocess
from helper import Helper
from instance_manager import MasterManager


class MasterListManager:

    def __init__(self, minion_config, poll_cycle, service_name, region):
        #print "%s, %s, %s" % (minion_config, poll_cycle, service_name)
        self.config = minion_config
        self.sleep_time = poll_cycle
        self.service_name = service_name
        self.region = region
        
    def get_masters_from_config(self):
        masters= []
        try:
            info_yaml = yaml.load(open(self.config, "r").read())
            masters = info_yaml.get('master', [])
        except Exception, e:
            raise
        return masters
        
    def get_masters_from_dynamodb(self):
        '''retrieve and return the list of active salt masters from dynamodb'''
        # active = status==LAUNCH, ipaddr != no-ip-yet
        master_ipaddrs = []
        try:
            m = MasterManager(region)
            masters = m.get_active()
            #print masters
            for m in masters:
                master_ipaddrs.append(str(m.ipaddr))
        except Exception, e:
            raise
        return sorted(master_ipaddrs)
        
    def update_config(self, masters_list):
        '''update CONFIG_FILE with active salt masters if needed'''
        try:
            info_yaml = yaml.load(open(self.config, "r").read())
            info_yaml['master'] = masters_list
            with open(self.config, 'w') as yaml_file:
                yaml_file.write( yaml.dump (info_yaml, default_flow_style=False))
        except Exception, e:
            raise
        return

    def restart_service(self):
        '''restart the local salt-minion service'''
        result = False
        try:
            output = subprocess.check_output(["/usr/sbin/service", self.service_name, "restart"])
            #print "restarting service - %s" % self.service_name
        except:
            #print "Exception when restarting service [%s] status" % self.service_name
            raise
        return

    def update_config_if_needed(self):
        try:
            masters_in_config = self.get_masters_from_config()
            masters_in_dynamodb = self.get_masters_from_dynamodb()
            if masters_in_config != masters_in_dynamodb:
                self.update_config(masters_in_dynamodb)                
                self.restart_service()
        except Exception, e:
            raise

    def main(self):
        while True:
            try:
                self.update_config_if_needed()
                time.sleep(self.sleep_time)
            except:
                raise


if __name__ == "__main__":
    POLL_CYCLE = 30 # seconds to sleep between polling dynamodb for list of active salt masters
    CONFIG_FILE = "/etc/salt/minion"
    SVC_NAME = "salt-minion"
    h = Helper()
    region = h.get_region()
    mm = MasterListManager(CONFIG_FILE, POLL_CYCLE, SVC_NAME, region)
    try:
        mm.main()
    except Exception, e:
        print "Error occurred: %s" % e
        sys.exit(1)

