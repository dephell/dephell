# dephell project test

Test project package.

1. Get project dependencies from `from`.
1. Attach dependencies from `and`.
1. Build wheel package.
1. Detect pythons to run. By default, all installed pythons that supported by project. You can limit it by one python version with `--python`.
1. For every python:
    1. Make temporary virtual environment.
    1. Copy inside test files specified in `tests`.
    1. Install package from wheel.
    1. Install test command.
    1. Run command from `command` in config.

Use [dephell venv run](cmd-venv-run) instead of this command if you want to run tests for current code without many pythons, temporary environments, and creating package.

## Example

DepHell contains next environment in the config:

```bash
[tool.dephell.pytest]
# read dependencies from poetry format
from = {format = "poetry", path = "pyproject.toml"}
# copy files that requred for tests
tests = ["tests", "README.md"]
# run command `pytest`
command = "pytest -x tests/"
```

And next lines in the poetry config:

```bash
[tool.poetry]
name = "dephell"
version = "0.3.2"
# ...

[tool.poetry.dependencies]
python = ">=3.5"
# ...
```

You can run tests on this environment by the next command:

```bash
$ dephell project test --env=pytest
INFO creating wheel...
INFO get interpreters
INFO create venv (python=3.7.0)
INFO copy files (path=tests)
INFO copy files (path=README.md)
INFO install project (path=/home/gram/Documents/dephell/dist/dephell-0.3.2-py3-none-any.whl)
INFO executable not found, installing (executable=pytest)
INFO run tests (command=['pytest', '-x', 'tests/'])
...
```

If you have installed python 2.7, 3.5, 3.6, and 3.7 then this command will test your code on 3.5, 3.6, and 3.7. Also, you can explicitly specify required python:

```bash
dephell project test --traceback --env=pytest --python=3.7
```

## See also

1. [dephell venv run](cmd-venv-run) to run tests for current codebase without complicated isolation.
1. [dephell deps convert](cmd-deps-convert) for details how DepHell converts dependencies from one format to another.
1. [Python lookup](python-lookup) for details how you can specify Python version for commands.
1. [Full list of config parameters](params)
