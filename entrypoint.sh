#!/bin/sh

# Start nginx and JupyterHub
nginx && sudo -u jupyter /opt/jupyterhub-venv/bin/jupyterhub -f $JUPYTERHUB_CONFIG
