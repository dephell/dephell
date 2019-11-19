# dephell docker run

Run a command inside the Docker container.

```bash
$ sudo dephell docker run echo "Hello, world"

[sudo] password for gram:
INFO running... (container=dephell-dephell-nLn6-main, command=['echo', 'Hello, world'])
Hello, world
INFO done
```

If a command isn't specified, dephell will try to get it from [config](config):

```toml
[tool.dephell.main]
command = "echo 'Hello, world!'"
```

## See also

1. [dephell docker create](cmd-docker-create) to read how dephell creates a new container.
1. [dephell docker shell](cmd-docker-shell) to run a shell inside a container.
1. [dephell docker stop](cmd-docker-stop) to stop command execution inside a container.
