base:
  '*':
    - global

  'roles:webserver':
    - match: grain
    - webserver

  'roles:saltmaster':
    - match: grain
    - saltmaster
