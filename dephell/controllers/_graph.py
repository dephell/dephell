# built-in
from collections import ChainMap
from logging import getLogger
from typing import Optional

# app
from ..models.dependency import Dependency
from ..models.root import RootDependency


logger = getLogger(__name__)


class Layer:
    def __init__(self, level: int, *deps):
        self.level = level
        self._mapping = dict()
        for dep in deps:
            self.add(dep)

    def get(self, name: str):
        return self._mapping.get(name)

    def add(self, dep) -> None:
        if dep.name not in self._mapping:
            self._mapping[dep.name] = dep
            return

        # if it is the first layer (requiements.txt) try to merge these deps
        if self.level == 1:
            self._mapping[dep.name] += dep
            if not self._mapping[dep.name].compat:
                raise ValueError('Cannot resolve root dependency: ' + dep.name)
            return

        raise KeyError('Dependency already added in layer: ' + dep.name)

    def clear(self) -> None:
        for name, dep in self._mapping.copy().items():
            if not dep.used:
                del self._mapping[name]

    def copy(self) -> 'Layer':
        return type(self)(self.level, *self._mapping.values())

    # magic methods

    def __delitem__(self, name):
        del self._mapping[name]

    def __contains__(self, dep) -> bool:
        if not isinstance(dep, str):
            dep = dep.name
        return dep in self._mapping

    def __iter__(self):
        return iter(self._mapping.values())

    def __repr__(self):
        return '{name}({level})'.format(
            name=self.__class__.__name__,
            level=self.level,
        )


class Graph:
    conflict = None  # type: Optional[Dependency]

    def __init__(self, *roots):
        for root in roots:
            if not root.dependencies:
                logger.warning('empty root passed')
        self._roots = list(roots)
        self._layers = []
        self.reset()

    def reset(self) -> None:
        self._layers = [Layer(0, *self._roots)]
        self._deps = ChainMap(*[layer._mapping for layer in self._layers])
        self.conflict = None

    def clear(self) -> None:
        """Drop from graph all deps that isn't required for roots.
        """
        for layer in self._layers[1:]:
            layer.clear()

    def add(self, dep, *, level: Optional[int] = None) -> None:
        if isinstance(dep, RootDependency):
            self._layers[0].add(dep)
            self._roots.append(dep)
            return

        if level is not None:
            if level < len(self._layers):
                self._layers[level].add(dep)
            else:
                layer = Layer(level, dep)
                self._layers.append(layer)
                self._deps = self._deps.new_child(layer._mapping)
            return

        parents_names = dep.constraint.sources
        for layer in self._layers:
            for parent in layer:
                if parent.name in parents_names:
                    return self.add(dep, level=layer.level + 1)
        raise KeyError('cannot find any parent for dependency: ' + str(dep.name))

    def get_leafs(self, level: Optional[int] = None) -> tuple:
        """Get deps that isn't applied yet
        """
        layers = self._layers
        if level is not None:
            layers = layers[:level + 1]

        result = []
        for layer in layers:
            for dep in layer:
                if not dep.applied and dep.used:
                    result.append(dep)
        return tuple(result)

    def get_layer(self, dep_or_level) -> Layer:
        if isinstance(dep_or_level, int):
            return self._layers[dep_or_level]

        dep = dep_or_level
        for layer in reversed(self._layers):
            if dep in layer:
                return layer

        raise KeyError('cannot find dep')

    def get(self, name: str):
        if name in self._deps:
            return self._deps[name]
        for layer in reversed(self._layers):
            dep = layer.get(name)
            if dep is not None:
                return dep

    def get_children(self, dep) -> dict:
        """Get all children of dependency that already represented in graph.
        """
        if not dep.locked:
            return dict()
        result = dict()
        for child in dep.dependencies:
            layer = self.get_layer(child)
            if layer is None:
                continue
            if child.name in result:
                logger.warning('Recursive dependency: {dep}', extra=dict(dep=child.name))
            else:
                result[child.name] = self.get(name=child.name)
            result.update(self.get_children(child))
        return result

    def get_parents(self, *deps, avoid: Optional[list] = None) -> dict:
        if avoid is None:
            avoid = []

        parents = dict()
        for dep in deps:
            for layer in self._layers:
                for parent in layer:
                    was_locked = parent.locked
                    for children in parent.dependencies:
                        if children.name != dep.name:
                            continue
                        if children.name in avoid:
                            continue
                        parents[parent.name] = parent
                        break
                    # if dependency hasn't been locked then unlock it after our accidental lock
                    if parent.locked and not was_locked:
                        parent.unlock()
        if parents:
            parents.update(self.get_parents(
                *parents.values(),
                avoid=avoid + [dep.name for dep in deps],
            ))
        return parents

    def draw(self, path: str = '.dephell_report', suffix: str = '') -> None:
        from graphviz import Digraph
        from graphviz.backend import ExecutableNotFound

        dot = Digraph(
            name=self._roots[0].name + suffix,
            directory=path,
            format='png',
        )
        first_deps = self._layers[1]

        # add root nodes
        for root in self._roots:
            dot.node(root.name, root.raw_name, color='blue')

        # add nodes
        for dep in self:
            # https://graphviz.gitlab.io/_pages/doc/info/colors.html
            if self.conflict and dep.name == self.conflict.name:
                color = 'crimson'
            elif dep in first_deps:
                color = 'forestgreen'
            else:
                color = 'black'
            dot.node(dep.name, dep.raw_name + str(dep.constraint), color=color)

        # add edges
        for dep in self:
            for parent, constraint in dep.constraint.specs:
                dot.edge(parent, dep.name, label=constraint)

        # save files
        try:
            dot.render()
        except ExecutableNotFound as e:
            raise ImportError('GraphViz is not installed yet.') from e

    # properties

    @property
    def names(self) -> set:
        return set(self._deps.keys())

    @property
    def deps(self) -> tuple:
        return tuple(dep for dep in self._deps.values() if dep not in self._roots)

    @property
    def applied(self) -> bool:
        return all(root.applied for root in self._roots)

    @property
    def metainfo(self) -> RootDependency:
        return RootDependency.get_metainfo(*self._roots)

    # magic

    def __iter__(self):
        return iter(self.deps)

    def __contains__(self, dep) -> bool:
        if isinstance(dep, str):
            return dep in self.names
        return dep in self.deps

    def __repr__(self):
        roots = [str(root) for root in self._roots]
        return '{name}({roots})'.format(
            name=type(self).__name__,
            roots=', '.join(roots),
        )
