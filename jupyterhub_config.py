from traitlets import Unicode

from jupyterhub.handlers import LogoutHandler
from jhub_remote_user_authenticator.remote_user_auth import RemoteUserLoginHandler, RemoteUserAuthenticator

import os

venv_dir = '/opt/jupyterhub-venv'
jupyter_home = '/opt/jupyterhub'

# REMOTE_USER auth config
class MyLogoutHandler(LogoutHandler):

  async def render_logout_page(self):
    logout_endpoint = self.authenticator.logout_endpoint

    self.redirect(logout_endpoint)

class MyAuthenticator(RemoteUserAuthenticator):
  """
  Accept the authenticated user from the header, based on an Remote_User
  """

  logout_endpoint = Unicode(
    default_value='/logout',
    config=True,
    help="""URL to log the user out and clean the session""")

  def get_handlers(self, app):
    return [
      (r'/login', RemoteUserLoginHandler),
      (r'/logout', MyLogoutHandler),
    ]

c.JupyterHub.authenticator_class = MyAuthenticator
c.JupyterHub.shutdown_on_logout = True

c.AccessTokenAuthenticator.header_name = "REMOTE_USER"
c.AccessTokenAuthenticator.logout_endpoint = "/logout"

# Debug config

import logging
c.JupyterHub.log_level = logging.DEBUG
c.ConfigurableHTTPProxy.debug = True

# Spawner config

c.JupyterHub.spawner_class = 'sudospawner.SudoSpawner'
c.SudoSpawner.sudospawner_path = f'{venv_dir}/bin/sudospawner'

origin = "*" # can also be the specific URL of the JupyterHub proxy server (e.g. http://localhost:8080)
c.Spawner.args = [
  '--ServerApp.allow_origin={0}'.format(origin), # allow CORS from 'origin'
  '--transport=ipc' # use unix sockets to communicate with kernels
]
c.Spawner.env_keep = ['JUPYTERHUB_ACTIVITY_URL', 'JUPYTERHUB_SERVER_NAME', 'JUPYTERHUB_API_URL', 'JUPYTERHUB_API_TOKEN', 'JUPYTERHUB_SERVICE_URL', 'JUPYTERHUB_SINGLEUSER_APP', 'JUPYTERHUB_USER', 'JUPYTERHUB_GROUP', 'PYTHONPATH', 'PATH', 'CONDA_ROOT', 'CONDA_DEFAULT_ENV']

# Server config
c.JupyterHub.hub_bind_url = f"http+unix://%2Frun%2Fjupyterhub%2Fjupyterhub.sock"
c.JupyterHub.hub_connect_url = c.JupyterHub.hub_bind_url
c.JupyterHub.bind_url = "http+unix://%2Frun%2Fjupyterhub%2Fchp.sock"
c.JupyterHub.hub_socket_mode = 0o660
c.ConfigurableHTTPProxy.api_url = "http+unix://%2Frun%2Fjupyterhub%2Fchp-api.sock"

# We need to tell single-user servers that they need a special URL to connect to the Hub's API.
# This is because the single-user server runs as a normal user, and does not have access to the Hub's socket (see nginx.conf).
c.Spawner.environment.update({
  'JUPYTERHUB_API_URL': "http+unix://%2Fjupyterhub_public%2Fjupyterhub-api.sock/hub/api/",
  'JUPYTERHUB_ACTIVITY_URL': lambda spawner : f"http+unix://%2Fjupyterhub_public%2Fjupyterhub-api.sock/hub/api/users/{spawner.user.name}/activity"
})
c.JupyterHub.base_url = "/"

# Configure paths for essential server files
c.JupyterHub.cookie_secret_file = f"{jupyter_home}/jupyterhub_cookie_secret"
c.JupyterHub.db_url = f"sqlite://{jupyter_home}/jupyterhub.sqlite"
c.ConfigurableHTTPProxy.pid_file = f"{jupyter_home}/jupyter-proxy.pid"

c.Spawner.default_url = '/lab?reset'
c.Spawner.notebook_dir = '~'
