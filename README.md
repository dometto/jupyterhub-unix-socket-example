build with `docker build . -t jhub-uds`

run with `docker run --name jhub --rm -p 8080:80 localhost/jupyterhub-remote-unix-socket:latest`

Connect to http://localhost:8080 in your browser. You will be logged as user alice on the Hub.
