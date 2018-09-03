# ![DepHell](./assets/logo.png)

Dependency resolution for Python.

## Installation

```bash
sudo pip3 install dephell
```

## Usage

As CLI:

```bash
# output to stdout:
dephell requirements.txt
# output to file:
dephell requirements.in requirements.txt
```

As runnable module:

```bash
python3 -m dephell /path/to/requirements.txt output.txt
```

As python lib:

```python
from dephell import Resolver
resolver = Resolver.from_requirements(path_from)
resolver.resolve()
content = resolver.to_requirements()
```
