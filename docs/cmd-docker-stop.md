# dephell docker stop

The command stops the Docker container for a current project and environment. It works like [docker stop](https://docs.docker.com/engine/reference/commandline/stop/). If something (even shell) executes inside the container, it will be stopped. However, you won't lost created files and installed programs inside of the container. If you want to get rid of everything inside, use [dephell docker destroy](cmd-docker-destroy).

## See also
