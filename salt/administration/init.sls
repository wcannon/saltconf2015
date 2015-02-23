boto-sdk:
  pip.installed:
    - name: boto

docopt-install:
  pip.installed:
    - name: docopt

/var/spool/cron/crontabs/root:
  file:
    - append
    - text: "@reboot /usr/bin/python /etc/salt/ha/dns-update/dns-update.py"
