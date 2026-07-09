#!/bin/sh
nginx && sudo -u jupyter /opt/jupyterhub-venv/bin/jupyterhub -f $JUPYTERHUB_CONFIG