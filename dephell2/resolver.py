from collections import OrderedDict
from operator import attrgetter
from itertools import count

from .dependency import Dependency
from .release import Release
from .repositories import WareHouseRepo
from .root import RootDependency


Dependency.repo = WareHouseRepo()
Release.repo = WareHouseRepo()


class Resolver:
    def __init__(self, deps):
        self.graph = OrderedDict(('root', RootDependency(deps)))

    def apply(self, node):
        """Apply deps of passed node to graph
        """
        ...

    def get_parents(self, dep):
        """Get all deps which depend on passed dep
        """
        ...

    def check_mutation(self, dep, spec):
        """Do not apply one mutation twice
        """
        ...

    def mutate(self, dep):
        """Change one from parent deps for trying to resolve conflict.
        """
        ...

    def unapply(self, dep):
        """Unapply dep from child deps
        """
        for name, other in self.graph.items():
            if dep.normalized_name not in other.versions:
                continue
            other.unapply(dep.normalized_name)
            self.unapply(other)

    def get_layers(self):
        """Iterate by graph layers
        """
        last_layer = 0
        for layer in count(start=1):
            child = [node for node in self.graph if node.layer == last_layer]
            if not child:
                return
            yield child

    def resolve(self):
        while True:
            for layer in self.get_layers():
                for node in layer:
                    # apply dep to it's child deps
                    conflict = self.apply(node)
                    if conflict is None:
                        continue

                    # mutate on of the parent deps
                    mutated = self.mutate(conflict)
                    self.unapply(mutated)
                    # apply all layers from root
                    break
            else:
                # if we iterated through all layers, this is the Victory
                return
