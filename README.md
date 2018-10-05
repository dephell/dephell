# ![DepHell](./assets/logo.png)

Dependency resolution for Python.

## Installation

```bash
sudo pip3 install dephell
```


## CLI usage

```bash
python3 -m dephell convert <from-format> <from-path> <to-format> <to-path>
```

Example:

```bash
python3 -m dephell convert pip requirements.in pip requirements.txt
```

Available formats:

1. `pip` -- [pip's requirements file](https://pip.pypa.io/en/stable/user_guide/#id1).
1. `pipfile` -- not locked [Pipfile](https://github.com/pypa/pipfile#pipfile)


## Python lib usage

```python
from dephell import Resolver
resolver = Resolver.from_requirements(path_from)
resolver.resolve()
content = resolver.to_requirements()
```


## TODO

1. Pipfile.lock
1. poetry
1. poetry lock
1. environments
1. Python version
1. Zero release (compatible with any constraints)
1. url defined release
1. git based dependency
1. Beautiful CLI
