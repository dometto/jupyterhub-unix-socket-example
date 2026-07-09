Secure Nginx -> ConfigurableHTTPProxy -> JupyterHub (with REMOTE_USER authentication) using Unix Domain Sockets

build with `docker build . -t jupyterhub-remote-unix-socket`

run with `docker run --name jhub --rm -p 8080:80 localhost/jupyterhub-remote-unix-socket:latest`

Connect to http://localhost:8080 in your browser. You will be logged in as user `alice` on the Hub.

## Usecase

This is a demonstration of how to run JupyterHub and ConfigurableHTTPProxy on Unix Domain Sockets, with Nginx proxying requests from outside to CHP. Nginx passes on a REMOTE_USER http header, which is assumed to orginate from a (trusted) upsteam authentication server.

The rationale for this is to keep users (on this test container, `alice` and `bob`) from being able to spawn users as another user. This would be possible if JupyterHub or CHP were listening on TCP sockets, and if `alice` and `bob` have shell access to the machine. With Unix Domain Sockets, we prevent `alice` and `bob` from directly connecting to the sockets on which our servers run.

So this is useful only when:

- running JupyterHub+Nginx on a VM with multiple users
- spawning singleuser servers on the same VM (not e.g. as separate containers in a k8s cluster)
- authentication and authorization are outsourced to an upstream auth server which passes on a REMOTE_USER header to Nginx

So the threat model against which this guards is semi-trusted users working together on the same machine (e.g. members of a large research group, + students) being able to gain access to each others' data. If anyone has or gains root access to the machine, of course that person will be able to access all users' singleuser servers and data.

We use `sudospawner` to prevent having to run `jupyterhub` as root.

## Todo

- Better explanation in this README>-
- Add tests to prove that `alice` can't spawn a server as `bob`
- In the nginx config for the public jupyterhub socket, make nginx only process requests to `/hub/api`.
