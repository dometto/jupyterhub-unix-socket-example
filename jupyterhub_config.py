from traitlets import Unicode
from jupyterhub.handlers import LogoutHandler
from jhub_remote_user_authenticator.remote_user_auth import RemoteUserLoginHandler, RemoteUserAuthenticator
import os

venv_dir = '/opt/jupyterhub-venv'  # Directory for the virtual Python environment
jupyter_home = '/opt/jupyterhub'  # Base directory for JupyterHub's persistent files

# Remote User Authentication
# This setup authenticates users based on an external system, referenced by the REMOTE_USER environment header.
class MyLogoutHandler(LogoutHandler):
    """
    Redirects users to a specific logout endpoint when logging out from JupyterHub.
    """
    async def render_logout_page(self):
        logout_endpoint = self.authenticator.logout_endpoint
        self.redirect(logout_endpoint)

class MyAuthenticator(RemoteUserAuthenticator):
    """
    Authenticator for accepting pre-authenticated users provided via REMOTE_USER header.
    Suitable for systems relying on an upstream identity provider.
    """
    logout_endpoint = Unicode(
        default_value='/logout',
        config=True,
        help="""Logout URL where sessions are invalidated"""
    )

    def get_handlers(self, app):
        return [
            (r'/login', RemoteUserLoginHandler),
            (r'/logout', MyLogoutHandler),
        ]

c.JupyterHub.authenticator_class = MyAuthenticator

# Specify which HTTP header to parse during authentication
c.AccessTokenAuthenticator.header_name = "REMOTE_USER"
c.AccessTokenAuthenticator.logout_endpoint = "/logout"

# Debugging options to enable verbose logging
import logging
c.JupyterHub.log_level = logging.DEBUG
c.ConfigurableHTTPProxy.debug = True

# Custom Spawner Configurations
c.JupyterHub.spawner_class = 'sudospawner.SudoSpawner'  # Allows launching user environments securely
c.SudoSpawner.sudospawner_path = f'{venv_dir}/bin/sudospawner'  # Binary path for the SudoSpawner

# Allow cross-origin requests optionally and use UDS for comminication with kernels
origin = "*"  # Allow all origins, can be restricted by specific instances
c.Spawner.args = [
    '--ServerApp.allow_origin={0}'.format(origin),  # Additional security headers
    '--transport=ipc'  # Communications via safe socket-based exchange
]

# Specify essential system variables for a consistent user-server interaction lifecycle
c.Spawner.env_keep = [
    'JUPYTERHUB_ACTIVITY_URL', 'JUPYTERHUB_SERVER_NAME', 'JUPYTERHUB_API_URL',
    'JUPYTERHUB_API_TOKEN', 'JUPYTERHUB_SERVICE_URL',
    'JUPYTERHUB_SINGLEUSER_APP', 'JUPYTERHUB_USER', 'JUPYTERHUB_GROUP',
    'PYTHONPATH', 'PATH', 'CONDA_ROOT', 'CONDA_DEFAULT_ENV'
]

# Server Binding Information
# Hub listens and communicates over secure Unix sockets
c.JupyterHub.hub_bind_url = "http+unix://%2Frun%2Fjupyterhub%2Fjupyterhub.sock"
c.JupyterHub.hub_connect_url = c.JupyterHub.hub_bind_url
c.JupyterHub.bind_url = "http+unix://%2Frun%2Fjupyterhub%2Fchp.sock"
c.JupyterHub.hub_socket_mode = 0o660 # Set file permissions for Hub sockets
c.ConfigurableHTTPProxy.api_url = "http+unix://%2Frun%2Fjupyterhub%2Fchp-api.sock"

# Configure the single-user (notebook) servers so that they connect to the Hub's API via the public endpoint (no REMOTE_USER auth).
# See nginx.conf
c.Spawner.environment.update({
    'JUPYTERHUB_API_URL': "http+unix://%2Fjupyterhub_public%2Fjupyterhub-api.sock/hub/api/",   # Unix-path specific for backend API
    'JUPYTERHUB_ACTIVITY_URL': lambda spawner : f"http+unix://%2Fjupyterhub_public%2Fjupyterhub-api.sock/hub/api/users/{spawner.user.name}/activity"
})

# General config
c.JupyterHub.shutdown_on_logout = True
c.JupyterHub.base_url = "/"
c.JupyterHub.cookie_secret_file = f"{jupyter_home}/jupyterhub_cookie_secret"
c.JupyterHub.db_url = f"sqlite://{jupyter_home}/jupyterhub.sqlite"
c.ConfigurableHTTPProxy.pid_file = f"{jupyter_home}/jupyter-proxy.pid"

c.Spawner.default_url = '/lab?reset'
c.Spawner.notebook_dir = '~'
