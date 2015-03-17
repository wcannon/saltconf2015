apache:
  pkg:
    - name: apache2
    - installed
  service:
    - name: apache2
    - running
    - watch:
      - pkg: apache2

apache2-utils:
  pkg.installed

