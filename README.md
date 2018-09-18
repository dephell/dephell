# ![DepHell](./assets/logo.png)

Dependency resolution for Python.

## Installation

```bash
sudo pip3 install dephell
```


## CLI usage

```bash
python3 -m dephell convert [-tl|--to-lock] [--] <from-format> <from-path> <to-format> <to-path>
```

Example:

```bash
python3 -m dephell convert --to-lock pip requirements.in pip requirements.txt
```

Available formats:

1. `pip` -- [pip's requirements file](https://pip.pypa.io/en/stable/user_guide/#id1).


## Python lib usage

```python
from dephell import Resolver
resolver = Resolver.from_requirements(path_from)
resolver.resolve()
content = resolver.to_requirements()
```
