# dephell project register

Register a project in the system or in a venv.

What the command does:

1. Creates [egg-info](https://setuptools.readthedocs.io/en/latest/formats.html#eggs-and-their-formats) in the root of the given project.
1. Creates [egg-link](https://setuptools.readthedocs.io/en/latest/formats.html#egg-links) that points on the created egg-info.
1. Creates a record in [pth file](https://docs.python.org/3/library/site.html) (named `dephell.pth`) to make the project importable.

Note that it doesn't install any dependencies. Despite that, the command is quite similar to what `pip install -e .` and `python3 setup.py develop` do.

## In a global interpreter

Register the current project in a global Python interpreter:

```bash
dephell project register
```

Explicitly specify python interpreter to register in:

```bash
dephell project register  --python=3.6
```

See also [how DepHell choice Python interpreter by default](python-lookup).

## In a venv

Register the current project in the `main` venv of the current project:

```bash
dephell project register .
```

Register another project in the `main` env of the current project:

```bash
dephell project register ./some/path/ /another/path/
```

Register another project in the `pytest` env of the current project:

```bash
dephell project register --env=pytest ./path/to/project/
```

Register the current project in a specific venv:

```bash
dephell project register --venv=./path/to/venv .
```

Dephell uses `from` of the current project by default. You can explicitly specify another one:

```bash
dephell project register --from-format=poetry --from-path=pyproject.toml ./path/to/a/project/
```

## See also

1. [dephell deps install](cmd-deps-install) to install dependencies of a project.
1. [dephell deps install](cmd-deps-install) to install dependencies of a project.
1. [Python lookup](python-lookup) for details how you can specify Python version for commands.
1. [Full list of config parameters](params)
