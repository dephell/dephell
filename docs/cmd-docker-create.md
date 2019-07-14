# dephell docker create

Create a new docker container for the project. Usually, you don't need to call this command directly because all other commands in [dephell docker](index-docker) group (except [dephell docker destroy](cmd-docker-destroy)) will create container if it doesn't exist.

```bash
$ sudo dephell docker create
INFO creating container for project... (container=dephell-dephell-nLn6-main)
INFO image not found, pulling... (repository=python, tag=latest)
INFO pulled
INFO container created
```

By default, the command creates container with authogenerated name (based on project path and current environment) from [python:latest](https://hub.docker.com/_/python) You can specify these parameters in [dephell config](config):

```toml
[tool.dephell.main.docker]
container = "container-name"
repo = "python"
tag = "3.7.4-stretch"
```

## See also
