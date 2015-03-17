base:
  '*':
    - global

  'roles:administration':
    - match: grain
    - administration

  'roles:webserver':
    - match: grain
    - apache
