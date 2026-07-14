#!/bin/sh

# Check read/write permissions on UDS sockets for normal users
# Test socket permissions with bob

# Define socket paths
CHP_SOCKET="/run/jupyterhub/chp.sock"
CHP_API_SOCKET="/run/jupyterhub/chp-api.sock"
JUPYTERHUB_SOCKET="/run/jupyterhub/jupyterhub.sock"
PUBLIC_ENDPOINT_SOCKET="/jupyterhub_public/jupyterhub-api.sock"

for SOCKET in "$CHP_SOCKET" "$CHP_API_SOCKET" "$JUPYTERHUB_SOCKET"; do
  if sudo -u bob [ -r "$SOCKET" ] || sudo -u bob [ -w "$SOCKET" ]; then
    echo "Failure: bob should not have access to $SOCKET"
    exit 1
  else
    echo "Hoorah! bob does not have access to $SOCKET"
  fi
done

if ! (sudo -u bob [ -r "$PUBLIC_ENDPOINT_SOCKET" ] && sudo -u bob [ -w "$PUBLIC_ENDPOINT_SOCKET" ]); then
  echo "Failure: bob should have read/write access to $PUBLIC_ENDPOINT_SOCKET"
  exit 1
else
  echo "Hoorah! bob has access to $PUBLIC_ENDPOINT_SOCKET"
fi
