boto-sdk:
  pip.installed:
    - name: boto

docopt-install:
  pip.installed:
    - name: docopt

/var/spool/cron/crontabs/root:
  file:
    - append
    - text: "@reboot /usr/bin/python /etc/salt/ha/dns-update/dns_update.py"

/etc/init/aws_im.conf:
  file:
    - managed
    - source: salt://administration/files/aws_im.conf
    - user: root
    - group: root
    - mode: 644

aws_im:
  service:
    - name: aws_im
    - running
    - enable: True
    - watch:
      - file: /etc/init/aws_im.conf

