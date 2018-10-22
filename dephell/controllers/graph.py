from logging import getLogger
from collections import ChainMap

from graphviz import Digraph


logger = getLogger(__name__)


class Layer:
    def __init__(self, level, *deps):
        self.level = level
        self._mapping = dict()
        for dep in deps:
            self.add(dep)

    def get(self, name: str):
        return self._mapping.get(name)

    def add(self, dep) -> None:
        if dep.name in self._mapping:
            raise KeyError('Dependency already added in layer')
        self._mapping[dep.name] = dep

    def clear(self) -> None:
        self._mapping = {name: dep for name, dep in self._mapping.items() if dep.used}

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
    def __init__(self, root):
        self.root = root
        if not root.dependencies:
            logger.warning('empty root passed')
        self.reset()

    def reset(self):
        self._layers = [Layer(0, self.root)]
        self._deps = ChainMap(*[layer._mapping for layer in self._layers])
        self.conflict = None

    def clear(self):
        """Drop from graph all deps that isn't required for roots.
        """
        for layer in self._layers[1:]:
            layer.clear()

    def add(self, dep, *, level=None):
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
        raise KeyError('Can\'t find any parent for dependency')

    def get_leafs(self) -> tuple:
        """Get deps that isn't applied yet
        """
        result = []
        for layer in self._layers:
            for dep in layer:
                if not dep.applied:
                    result.append(dep)
        return tuple(result)

    def get_layer(self, dep_or_level) -> Layer:
        if isinstance(dep_or_level, int):
            return self._layers[dep_or_level]

        dep = dep_or_level
        for layer in reversed(self._layers):
            if dep in layer:
                return layer

    def get(self, name):
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
                logger.warning('Recursive dependency: {}'.format(child))
            else:
                result[child.name] = child
            result.update(self.get_children(child))
        return result

    def get_parents(self, *deps, avoid=None) -> dict:
        if avoid is None:
            avoid = []

        parents = dict()
        for dep in deps:
            for layer in self._layers:
                for parent in layer:
                    for children in parent.dependencies:
                        if children.name != dep.name:
                            continue
                        if children.name in avoid:
                            continue
                        parents[parent.name] = parent
                        break
        if parents:
            parents.update(self.get_parents(
                *parents.values(),
                avoid=avoid + [dep.name for dep in deps]
            ))
        return parents

    def draw(self, path: str='.dephell_report', suffix: str=''):
        dot = Digraph(
            name=self.root.name + suffix,
            directory=path,
            format='png',
        )
        for dep in self:
            dot.node(dep.name, dep.raw_name + str(dep.constraint))
        for dep in self:
            for parent in dep.constraint.sources:
                dot.edge(parent, dep.name)
        dot.render()

    # properties

    @property
    def names(self) -> set:
        return set(self._deps.keys())

    @property
    def deps(self) -> tuple:
        return tuple(dep for dep in self._deps.values() if dep is not self.root)

    # magic

    def __iter__(self):
        return iter(self.deps)

    def __contains__(self, dep):
        if isinstance(dep, str):
            return dep in self.names
        return dep in self.deps
