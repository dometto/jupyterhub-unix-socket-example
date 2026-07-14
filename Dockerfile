# Use a lightweight nginx image as the base
FROM nginx:alpine

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    JUPYTER_HOME=/opt/jupyterhub \
    VENV_DIR=/opt/jupyterhub-venv \
    JUPYTERHUB_CONFIG=$JUPYTER_HOME/jupyterhub_config.py 

# Add users and create hub homedir
RUN addgroup -S jupyter && \
    adduser -S jupyter -G jupyter && \
    mkdir -p $JUPYTER_HOME /etc/jupyterhub && \
    chown jupyter:jupyter $JUPYTER_HOME && \
    addgroup jupyterhub && \
    adduser -D alice -G jupyterhub && \
    adduser -D bob -G jupyterhub

# Create /run/jupyterhub directory to save CHP and Hub sockets in
# They must be readable and writeable by both nginx and jupyter.
# We set the group to nginx and use setgid (chmod 02..) so that sockets created in this directory will have group nginx.
# Also create /jupyterhub_public as a directory containing a socket to for single-user servers to connect to JupyterHub's API, accessible by nginx and group jupyterhub.
RUN mkdir -p /run/jupyterhub && \
    chown jupyter:nginx /run/jupyterhub && \
    chmod 02770 /run/jupyterhub && \
    mkdir /jupyterhub_public && \
    chown nginx:jupyterhub /jupyterhub_public && \
    chmod 02770 /jupyterhub_public

# Install required packages
RUN apk add --no-cache \
    python3 \
    py3-pip \
    py3-virtualenv \
    git \
    nodejs \
    npm \
    sudo

# Create rule for sudospawner
RUN echo "jupyter ALL=(%jupyterhub)NOPASSWD: /opt/jupyterhub-venv/bin/sudospawner" > /etc/sudoers.d/allow-jupyter-jupyterhub

# Create and activate virtual environment, then install JupyterHub from Git
RUN python3 -m venv $VENV_DIR && \
    $VENV_DIR/bin/pip install --upgrade pip && \
    $VENV_DIR/bin/pip install git+https://github.com/jupyterhub/jupyterhub.git@d8735c479657947575678791f20171a9e7123166 && \
    $VENV_DIR/bin/pip install jhub-remote-user-authenticator==0.1.0 && \
    $VENV_DIR/bin/pip install sudospawner && \
    $VENV_DIR/bin/pip install jupyterlab

# Install configurable http proxy
RUN npm install -g configurable-http-proxy

# Copy default nginx configuration
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Copy a placeholder custom JupyterHub configuration, can be overridden
COPY jupyterhub_config.py $JUPYTERHUB_CONFIG

COPY entrypoint.sh /entrypoint.sh

# Expose port 80
EXPOSE 80

# Command to run nginx and JupyterHub
ENTRYPOINT /entrypoint.sh
