# dephell venv run

Runs command in the virtual environment of current project and environment.

1. If the virtual environment doesn't exist DepHell will [create it](cmd-venv-create).
1. If script doesn't exist in the virtual environment DepHell tries to install it from [PyPI](https://pypi.org/).

For example, get help for `sphinx-build` from `docs` environment of current project:

```bash
$ dephell venv run --env=docs sphinx-build --help
```

Command can be specified in the config:

```toml
[tool.dephell.docs]
command = "sphinx-build --help"
```

In this case command can be omitted:

```bash
$ dephell venv run --env=docs
```
