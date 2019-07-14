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
