# ![DepHell](./assets/logo.png)

Dependency resolution for Python.

## Installation

```bash
sudo pip3 install dephell
```

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
