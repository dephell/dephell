# dephell inspect venv

Shows information about virtual environment for current project and environment.

```bash
$ dephell inspect venv
{
  "activate": "/home/gram/.local/share/dephell/venvs/dephell-nLn6/main/bin/activate",
  "bin": "/home/gram/.local/share/dephell/venvs/dephell-nLn6/main/bin",
  "exists": true,
  "lib": "/home/gram/.local/share/dephell/venvs/dephell-nLn6/main/lib/python3.7/site-packages",
  "lib_size": "32.93Mb",
  "project": "/home/gram/Documents/dephell",
  "python": "/home/gram/.local/share/dephell/venvs/dephell-nLn6/main/bin/python3.7",
  "venv": "/home/gram/.local/share/dephell/venvs/dephell-nLn6/main"
}
```

Specify `--env` to get information about other environment:

```bash
$ dephell inspect venv --env=docs
```

Specify `--filter` to get one field from command output:

```bash
$ dephell inspect venv --filter=project
/home/gram/Documents/dephell
```

## See also

1. [dephell venv create](cmd-venv-create) for information about virtual environments management in DepHell.
1. [dephell inspect config](cmd-inspect-config) to get information about config parameters like venv path template.
1. [How to filter commands JSON output](filters).
