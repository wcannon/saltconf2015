highstate_run:
  local.state.highstate:
    - tgt: {{ data['id'] }}
