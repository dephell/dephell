# dephell deps convert

Convert dependencies between formats. Dephell will automagically lock them if needed and resolve all conflicts. Dependency resolution is the strongest side of the DepHell, pip and pipenv has no any dependency resolution that would be smart enough.

You can specify input and output in three different ways:

1. Explicitly specify path and format: `--from-format=poetry --from-path=pyproject.toml` and `--to-format=setuppy --to-path=setup.py`.
1. Specify only path: `--from=pyproject.toml` and `--to=setup.py`.
1. Specify only format: `--from=poetry` and `--to=setuppy`.

## Supported formats

1. Archives:
    1. [*.egg-info](https://setuptools.readthedocs.io/en/latest/formats.html) (`egginfo`)
    1. [*.tar.gz](https://packaging.python.org/glossary/#term-distribution-package) (`sdist`)
    1. [*.whl](https://pythonwheels.com) (`wheel`)
1. [pip](https://pip.pypa.io/en/stable/):
    1. [requirements.txt](https://pip.pypa.io/en/stable/user_guide/#requirements-files) (`pip`)
    1. [requirements.lock](https://nvie.com/posts/pin-your-packages/) (`piplock`)
1. [pipenv](https://pipenv.readthedocs.io/en/latest/):
    1. [Pipfile](https://github.com/pypa/pipfile) (`pipfile`)
    1. [Pipfile.lock](https://stackoverflow.com/a/49867443/8704691) (`pipfilelock`)
1. [poetry](https://github.com/sdispater/poetry):
    1. [pyproject.toml](https://poetry.eustace.io/docs/pyproject/) (`poetry`)
    1. [poetry.lock](https://poetry.eustace.io/docs/basic-usage/#installing-without-poetrylock) (`poetrylock`)
1. Other:
    1. [setup.py](https://docs.python.org/3/distutils/setupscript.html) (`setuppy`)
    1.[conda](https://conda.io/en/latest/)'s [environment.yml](https://docs.conda.io/projects/conda/en/latest/user-guide/tasks/manage-environments.html#creating-an-environment-file-manually) (`conda`)
    1. [pyproject.toml build-system requires](https://www.python.org/dev/peps/pep-0518/#build-system-table) (`pyproject`)
    1. Installed packages (`installed`). It works like [pip freeze](https://pip.pypa.io/en/stable/reference/pip_freeze/). Dephell can only read from this format, of course. If you want to install packages, use [install command](cmd-deps-install).

## Examples

Lock dependencies for Pipfile:

```bash
$ dephell deps convert --from=Pipfile --to=Pipfile.lock
```
Or the same, but more explicit:

```bash
$ dephell deps convert \
    --from-format=pipfile --from-path=Pipfile \
    --to-format=pipfilelock --to-path=Pipfile.lock
```

Best practice is specify your dependencies file in `pyproject.toml` DepHell config:

```bash
[tool.dephell.main]
from = {format = "pipfile", path = "Pipfile"}
to = {format = "pipfilelock", path = "Pipfile.lock"}
```

And after that DepHell will automatically detect your dependencies file:

```bash
$ dephell deps convert
```

See [configuration documentation](config) for more details.

## More examples

You can convert anything to anything:

1. Lock requirements.txt: `dephell deps convert --from=requirements.in --to=requirements.txt`
1. Lock Pipfile: `dephell deps convert --from=Pipfile --to=Pipfile.lock`
1. Lock poetry: `dephell deps convert --from=pyproject.toml --to=poetry.lock`
1. Migrate from setup.py to poetry: `dephell deps convert --from=setup.py --to=pyproject.toml`
1. Migrate from pipenv to poetry: `dephell deps convert --from=Pipenv --to=pyproject.toml`
1. Generate setup.py for poetry (to make project backward compatible with setuptools): `dephell deps convert --from=pyproject.toml --to=setup.py`
1. Generate requirements.txt from Pipfile to work on a pipenv-based project without pipenv: `dephell deps convert --from=Pipenv --to=requirements.txt`
1. Generate requirements.txt from poetry to work on a poetry-based project without poetry: `dephell deps convert --from=pyproject.toml --to=requirements.txt`

## Filter dependencies

You can filter dependencies by envs with `--envs` flag. All dependencies included in `main` or `dev` env. Also, some dependencies can be included in [extras](https://setuptools.readthedocs.io/en/latest/setuptools.html#declaring-extras-optional-features-with-their-own-dependencies). There is an example of poetry config with envs in comments:

```toml
[tool.poetry.dependencies]
python = ">=3.5"
aiohttp = "*"       # main, asyncio
textdistance = "*"  # main

[tool.poetry.dev-dependencies]
pytest = "*"    # dev, tests
sphinx = "*"    # dev

[tool.poetry.extras]
asyncio = ["aiohttp"]
tests = ["pytest"]
```

Examples, how to filter these deps:

```bash
$ dephell deps convert --envs main
# aiohttp, textdistance

$ dephell deps convert --envs asyncio
# aiohttp

$ dephell deps convert --envs main tests
# aiohttp, textdistance, pytest
```

## See also

1. [dephell project build](cmd-deps-install) to fast convert dependencies into setup.py, sdist and wheel.
1. [dephell deps install](cmd-deps-install) to install project dependencies.
1. [dephell deps tree](cmd-deps-tree) to show dependencies tree for project.
