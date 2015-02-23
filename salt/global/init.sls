#sleep 20:
#  cmd.run

ntp:
  pkg:
    - installed

Etc/UTC:
  timezone.system:
    - utc: True

python-psutil:
  pkg:
    - installed

git:
  pkg:
    - installed

nmap:
  pkg:
    - installed

screen:
  pkg:
    - installed

sysstat:
  pkg:
    - installed

unzip:
  pkg:
    - installed

iptraf:
  pkg:
    - installed

ethstatus:
  pkg:
    - installed

tcpdump:
  pkg:
    - installed

strace:
  pkg:
    - installed

htop:
  pkg:
    - installed

python-pip:
  pkg:
    - installed

# xfs filesystem software
xfsprogs:
  pkg:
    - installed
xfsdump:
  pkg:
    - installed

# cmd.run --> so we can see the last time a highstate was run on a server
date > /etc/salt/last_highstate_run:
  cmd:
    - run
