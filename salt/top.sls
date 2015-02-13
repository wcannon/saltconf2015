base:
  '*':
    - global

  'roles:webserver':
    - match: grain
    - apache
