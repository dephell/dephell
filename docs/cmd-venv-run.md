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

## Environment variables

This command passes next [environment variables](https://en.wikipedia.org/wiki/Environment_variable) into running command:

1. Your current environment variables.
1. Values from `vars` in config.
1. Values from [.env](https://github.com/theskumar/python-dotenv) file.

example of `.env` file:

```bash
export POSTGRES_USERNAME="dephell"
export POSTGRES_PASSWORD="PasswordExample"
export POSTGRES_URL="psql://$POSTGRES_USERNAME:$POSTGRES_PASSWORD@localhost"
```

DepHell supports any format of `.env` file: `export` word optional, quotes optional, `=` can be surrounded by spaces. However, we recommend to use above format, because it allows you to use [source command](https://bash.cyberciti.biz/guide/Source_command) to load these variables in your current shell.

Features for `.env` file:

1. Parameters expansion. In the example above `POSTGRES_URL` value will be expanded into `psql://dephell:PasswordExample@localhost`. If variable does not exist DepHell won't touch it. You can explicitly escape $ sign (`\$`) to avoid expansion.
1. Escape sequences. You can insert escape sequences like `\n` in values, and DepHell will process it.

Config example:

```toml
[tool.dephell.main]
vars = {PYTHONPATH = "."}
command = "python"

[tool.dephell.flake8]
vars = {TOXENV = "flake8"}
command = "tox"
```

Use `.env` for secret things like database credentials and `vars` in config for some environment-specific settings for running commands like environment for flake.

If you want to pass temporary variable that not intended to be stored in any file then just set this variable in your current shell:

```bash
$ CHECK=me dephell venv run python -c "print(__import__('os').environ['CHECK'])"
INFO running...
me
INFO command successfully completed
```

## See also

1. [dephell venv shell](cmd-venv-shell) to activate virtual environment for your current shell.
