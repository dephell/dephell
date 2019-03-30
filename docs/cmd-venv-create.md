# dephell venv create

Create virtual environment for current project and environment. Always create virtual environment before executing [dephell deps install](cmd-deps-install) or [dephell install](cmd-install) if you want them to install packages into special virtual environment. Otherwise, these commands will use your current virtual environment (or global interpreter).

Path to virtual environment contains these substitutions:

+ `{project}` will be replaced by the project name (name of path from `project` option, this is name of the current directory by default).
+ `{digest}` will be replaced by the short 4-letters digest of the project path to avoid conflicts for the projects with the same name in different locations.
+ `{env}` will be replaced by current environment (`main` by default).

For example, create virtual environment for `docs` environment of current project:

```bash
$ dephell venv create --env=docs
```

Get venv path template with [dephell inspect config](cmd-inspect-config) command:

```bash
$ dephell inspect config venv
/home/gram/.local/share/dephell/venvs/{project}-{digest}/{env}
```

Get path to the current venv (if created) with [dephell inspect venv](cmd-inspect-venv) command:

```bash
$ dephell inspect venv venv
/home/gram/.local/share/dephell/venvs/dephell-nLn6/main
```
