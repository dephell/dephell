from collections import OrderedDict
from .dependency import Dependency
from .release import Release
from .repositories import WareHouseRepo
from .root import RootDependency


Dependency.repo = WareHouseRepo()
Release.repo = WareHouseRepo()


class Resolver:
    def __init__(self, deps):
        self.graph = OrderedDict(('root', RootDependency(deps)))

    def apply(self, dep):
        """Apply deps of passed dep to graph
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
        ...

    def resolve(self):
        while True:
            for layer in self.get_layers():
                for dep in layer:
                    # apply dep to it's child deps
                    conflict = self.apply(dep)
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
