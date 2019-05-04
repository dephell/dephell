# Configuration and parameters

Dephell makes config from 3 layers:

1. Default parameters.
1. Section from config file.
1. CLI arguments.

## Config file

Config should be TOML file with `dephell.tool.ENV_NAME` sections (see [PEP-518](https://www.python.org/dev/peps/pep-0518/#tool-table)).

1. Default filename: `pyproject.toml`. You can change it by `--config` argument.
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

## See also

1. [`inspect config` command](cmd-inspect-config) to discover how dephell makes config for your project.
1. [dephell's own config](https://github.com/dephell/dephell/blob/master/pyproject.toml) to see real and full example.
