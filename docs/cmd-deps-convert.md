# dephell deps convert

Convert dependencies between formats. Dephell will automagically lock them if needed and resolve all conflicts.

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
    1. [pyproject.toml build-system requires](https://www.python.org/dev/peps/pep-0518/#build-system-table) (`pyproject`)
    1. Installed packages (`installed`). It works like [pip freeze](https://pip.pypa.io/en/stable/reference/pip_freeze/). Dephell can only read from this format, of course. If you want to install packages, use `install` command.
