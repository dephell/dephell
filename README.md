# ![DepHell](./assets/logo.png)

[![MIT License](https://img.shields.io/pypi/l/dephell.svg)](https://github.com/dephell/dephell/blob/master/LICENSE)
[![Travis CI](https://travis-ci.org/dephell/dephell.svg?branch=master)](https://travis-ci.org/dephell/dephell)
[![Powered by DepHell](./assets/badge.svg)](./docs/badge.md)

**DepHell** -- dependency management for Python.

+ Manage dependencies: [convert between formats](https://dephell.readthedocs.io/en/latest/cmd-deps-convert.html), [install](https://dephell.readthedocs.io/en/latest/cmd-deps-install.html), lock, [add new](https://dephell.readthedocs.io/en/latest/cmd-deps-add.html), resolve conflicts.
+ Manage virtual environments: [create](https://dephell.readthedocs.io/en/latest/cmd-venv-create.html), [remove](https://dephell.readthedocs.io/en/latest/cmd-venv-destroy.html), [inspect](https://dephell.readthedocs.io/en/latest/cmd-inspect-venv.html), [run shell](https://dephell.readthedocs.io/en/latest/cmd-venv-shell.html), [run commands inside](https://dephell.readthedocs.io/en/latest/cmd-venv-run.html).
+ [Install CLI tools](https://dephell.readthedocs.io/en/latest/cmd-jail-install.html) into isolated environments.
+ Manage packages: [install](https://dephell.readthedocs.io/en/latest/cmd-package-install.html), [list](https://dephell.readthedocs.io/en/latest/cmd-package-list.html), [search](https://dephell.readthedocs.io/en/latest/cmd-package-search.html) on PyPI.
+ [Build](https://dephell.readthedocs.io/en/latest/cmd-project-build.html) packages (to upload on PyPI), [test](https://dephell.readthedocs.io/en/latest/cmd-project-test.html), [bump project version](https://dephell.readthedocs.io/en/latest/cmd-project-bump.html).
+ [Discover licenses](https://dephell.readthedocs.io/en/latest/cmd-deps-licenses.html) of all project dependencies, show [outdated](https://dephell.readthedocs.io/en/latest/cmd-deps-outdated.html) packages, [find security issues](https://dephell.readthedocs.io/en/latest/cmd-deps-audit.html).
+ Generate [.editorconfig](https://dephell.readthedocs.io/en/latest/cmd-generate-editorconfig.html), [LICENSE](https://dephell.readthedocs.io/en/latest/cmd-generate-license.html), [AUTHORS](https://dephell.readthedocs.io/en/latest/cmd-generate-authors.html).

See [documentation](https://dephell.readthedocs.io/) for more details.

## Installation

Simplest way:

```bash
python3 -m pip install --user dephell[full]
```

See [installation documentation](https://dephell.readthedocs.io/en/latest/installation.html) for better ways.

## Usage

First of all, install DepHell and activate autocomplete:

```bash
python3 -m pip install --user dephell[full]
dephell autocomplete
```

Let's get [sampleproject](https://github.com/pypa/sampleproject) and make it better.

```bash
git clone https://github.com/pypa/sampleproject.git
cd sampleproject
```

This project uses [setup.py](https://docs.python.org/3/distutils/setupscript.html) for dependenciesand metainfo. However, this format over-complicated for most of projects. Let's convert it into [poetry](https://poetry.eustace.io/docs/pyproject/):

```bash
dephell deps convert --from=setup.py --to=pyproject.toml
```

It will make next `pyproject.toml`:

```toml
[tool.poetry]
name = "sampleproject"
version = "1.2.0"
description = "A sample Python project"
authors = ["The Python Packaging Authority <pypa-dev@googlegroups.com>"]
readme = "README.md"

[tool.poetry.scripts]
sample = "sample:main"

[tool.poetry.dependencies]
python = "!=3.0.*,!=3.1.*,!=3.2.*,!=3.3.*,<4,>=2.7"
coverage = {optional = true}
peppercorn = "*"

[tool.poetry.dev-dependencies]
check-manifest = "*"

[tool.poetry.extras]
test = ["coverage"]
```

Now, let's generate some useful files:

```bash
dephell generate authors

dephell generate license MIT

# https://editorconfig.org/
dephell generate editorconfig
```

Our users, probably, has no installed poetry, but they, definitely, has pip that can install files from setup.py. Let's make it easier to generate `setup.py` from our `pyproject.toml`. Also, it points for DepHell your default dependencies file. Add next lines in the `pyproject.toml`:

```toml
[tool.dephell.main]
from = {format = "poetry", path = "pyproject.toml"}
to = {format = "setuppy", path = "setup.py"}
```

You can see full real world example of config in [DepHell's own pyproject.toml](./pyproject.toml).

Now we can call DepHell commands without explicitly specifying `from` and `to`:

```bash
dephell deps convert
```

It will make setup.py and README.rst from pyproject.toml and README.md.

Now let's test our code into virtual environment:

```bash
$ dephell venv run pytest
WARNING venv does not exist, creating... (project=/home/gram/Documents/sampleproject, env=main, path=/home/gram/.local/share/dephell/venvs/sampleproject-Whg0/main)
INFO venv created (path=/home/gram/.local/share/dephell/venvs/sampleproject-Whg0/main)
WARNING executable does not found in venv, trying to install... (executable=pytest)
INFO build dependencies graph...
INFO installation...
# ... pip output
# ... pytest output
```

Also, we can just activate virtual environment for project and run any commands inside:

```bash
dephell venv shell
```

Ugh, we has tests, but has no `pytest` in our dependencies file. Let's add it:

```bash
dephell deps add --envs dev test -- pytest
```

Afer that our dev-dependencies looks like this:

```toml
[tool.poetry.dev-dependencies]
check-manifest = "*"
pytest = "*"

[tool.poetry.extras]
test = ["coverage", "pytest"]
```

One day we will have really many dependencies. Let's have a look how many of them we have now:

```bash
$ dephell deps tree
- check-manifest [required: *, locked: 0.37, latest: 0.37]
- coverage [required: *, locked: 4.5.3, latest: 4.5.3]
- peppercorn [required: *, locked: 0.6, latest: 0.6]
- pytest [required: *, locked: 4.4.0, latest: 4.4.0]
  - atomicwrites [required: >=1.0, locked: 1.3.0, latest: 1.3.0]
  - attrs [required: >=17.4.0, locked: 19.1.0, latest: 19.1.0]
  - colorama [required: *, locked: 0.4.1, latest: 0.4.1]
  - funcsigs [required: >=1.0, locked: 1.0.2, latest: 1.0.2]
  - more-itertools [required: <6.0.0,>=4.0.0, locked: 5.0.0, latest: 7.0.0]
    - six [required: <2.0.0,>=1.0.0, locked: 1.12.0, latest: 1.12.0]
  - more-itertools [required: >=4.0.0, locked: 7.0.0, latest: 7.0.0]
  - pathlib2 [required: >=2.2.0, locked: 2.3.3, latest: 2.3.3]
    - scandir [required: *, locked: 1.10.0, latest: 1.10.0]
    - six [required: *, locked: 1.12.0, latest: 1.12.0]
  - pluggy [required: >=0.9, locked: 0.9.0, latest: 0.9.0]
  - py [required: >=1.5.0, locked: 1.8.0, latest: 1.8.0]
  - setuptools [required: *, locked: 41.0.0, latest: 41.0.0]
  - six [required: >=1.10.0, locked: 1.12.0, latest: 1.12.0]
```

Hm... It is many or not? Let's look on their size.

```bash
$ dephell inspect venv --filter=lib_size
11.96Mb
```

Ugh... Ok, it's Python. Are they actual?

```bash
$ dephell deps outdated
[
  {
    "description": "More routines for operating on iterables, beyond itertools",
    "installed": [
      "5.0.0"
    ],
    "latest": "7.0.0",
    "name": "more-itertools",
    "updated": "2019-03-28"
  },
]
```

`Pytest` requires old version of `more-itertools`. That happens.

If our tests and dependencies are OK, it's time to deploy. First of all, increment project version:

```bash
$ dephell project bump minor
INFO generated new version (old=1.2.0, new=1.3.0)
```

And then build packages:

```bash
$ dephell project build
INFO dumping... (format=setuppy)
INFO dumping... (format=egginfo)
INFO dumping... (format=sdist)
INFO dumping... (format=wheel)
INFO builded
```

Now, we can upload these packages on [PyPI](https://pypi.org/) with [twine](https://github.com/pypa/twine/).

This is some of the most useful commands. See [documentation](https://dephell.readthedocs.io/) for more details.
