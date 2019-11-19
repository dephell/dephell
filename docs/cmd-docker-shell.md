# dephell docker shell

Run a shell inside of the Docker container for a current project and environment. Dephell tries to get the best shell in the following order:

1. zsh
1. bash
1. sh

The command is also useful for quick experiments with project in the isolated environment:

```bash
$ sudo dephell docker shell --docker-container=tmp
WARNING creating container... (container=tmp)
INFO openning shell... (container=tmp)
sh: 1: zsh: not found
root@d6ceb924fea6:/opt/project#
```

## See also

1. [dephell docker create](cmd-docker-create) to read how dephell creates a new container.
1. [dephell docker run](cmd-docker-run) to run a command inside a container.
