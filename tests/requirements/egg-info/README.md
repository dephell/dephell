# ![DepHell](./assets/logo.png)

Dependency resolution for Python.

## Installation

```bash
sudo pip3 install dephell
```

## CLI usage

With arguments:

```bash
python3 -m dephell convert \
    --from-format=pip --from-path=requirements.in \
    --to-format=piplock --to-path=requirements.txt
```

With config:

```bash
python3 -m dephell convert --config=pyproject.toml --env=main
```

Mix config and arguments:

```bash
python3 -m dephell convert --config=pyproject.toml \
    --to-format=piplock --to-path=requirements.txt
```

Available formats:

1. `pip` -- [pip's requirements file](https://pip.pypa.io/en/stable/user_guide/#id1).
1. `piplock` -- [locked](https://pip.pypa.io/en/stable/reference/pip_freeze/) pip's requirements file.
1. `pipfile` -- not locked [Pipfile](https://github.com/pypa/pipfile#pipfile)
1. `pipfilelock` -- locked [Pipfile](https://github.com/pypa/pipfile#pipfilelock)

## Python lib usage

```python
from dephell import PIPConverter, Requirement

loader = PIPConverter(lock=False)
resolver = loader.load_resolver(path='requirements.in')

resolver.resolve()
reqs = Requirement.from_graph(resolver.graph, lock=True)

dumper = PIPConverter(lock=True)
dumper.dump(reqs=reqs, path='requirements.txt')
```

## TODO

1. poetry
1. poetry lock
1. Python version
1. Zero release (compatible with any constraints)
1. url defined release
1. git based dependency
