# Configuration and parameters

Dephell makes config from 3 layers:

1. Default parameters.
1. Section from config file.
1. Environment variables.
1. CLI arguments.

## Config file

Config should be [TOML](https://github.com/toml-lang/toml) file with `tool.dephell.ENV_NAME` sections (see [PEP-518](https://www.python.org/dev/peps/pep-0518/#tool-table)).

1. By default, dephell tries to read `pyproject.toml` or `dephell.toml`. You can change it by `--config` argument.
1. Default environment: `main`. Environment is the name of the section inside of `tool.dephell` section in config file. You can change environment by `--env` argument.

Config example:

```toml
[tool.dephell.main]
# read from poetry format
from = {format = "poetry", path = "pyproject.toml"}
# drop dev-dependencies
envs = ["main"]
# and convert into setup.py
to = {format = "setuppy", path = "setup.py"}

[tool.dephell.pytest]
# read dependencies from setup.py
from = {format = "setuppy", path = "setup.py"}
# install main dependencies and `tests` extra dependencies
envs = ["main", "tests"]
# run command `pytest`
command = "pytest"
```

## CLI arguments

You can (re)define any config options with CLI arguments. For example, there is how you can define the same parameters as in the `pytest` section above:

```bash
$ dephell deps install \
    --from-format setuppy \
    --from-path setup.py \
    --envs main tests --

$ dephell deps run --command="pytest"

# Also for `venv run` you can specify command as positional argument:
$ dephell venv run pytest
```

It's OK for one-time actions, but for everyday usage we recommend to define config section for every kind of tasks you perform. For example, for dephell we have defined envs `main` to convert from poetry to setup.py, `flake8` for linting, `pytest` for tests, and `docs` for generating documentation. So, you can install and run test environment for dephell much simpler:

```bash
$ dephell venv create --env=pytest
$ dephell deps install --env=pytest
$ dephell venv run --env=pytest
```

Also, by default, DepHell uses `--env` to generate path to the virtual environment, so different `--env` values have different virtual environments.

## Environment variables

Sometimes, specifying config parameters in environment variables can be more suitable for you. Most common case is to set up `env` or path to config file. For example:

```bash
export DEPHELL_ENV=flake8
export DEPHELL_CONFIG="./project/dephell.toml"

# commands below will be executed with specified above env and path to config
dephell venv create
dephell deps install
dephell venv run

# do not forget to remove variables after all
unset DEPHELL_ENV
unset DEPHELL_CONFIG
```

DepHell do type casting in the same way as [dynaconf](https://dynaconf.readthedocs.io/en/latest/guides/environment_variables.html#precedence-and-type-casting). Just use TOML syntax for values:

```bash
# Numbers
DEPHELL_CACHE_TTL=42
DEPHELL_SDIST_RATIO=0.5

# Text
DEPHELL_FROM_FORMAT=pip
DEPHELL_FROM_FORMAT="pip"

# Booleans
DEPHELL_SILENT=true
DEPHELL_SILENT=false

# Use extra quotes to force a string from other type
DEPHELL_PYTHON="'3.6'"
DEPHELL_PROJECT="'true'"

# Arrays
DEPHELL_ENVS="['main', 'dev']"

# Dictionaries
DEPHELL_FROM='{format="pip", path="req.txt"}'
```

## See also

1. [`inspect config` command](cmd-inspect-config) to discover how dephell makes config for your project.
1. [dephell's own config](https://github.com/dephell/dephell/blob/master/pyproject.toml) to see real and full example.
