from collections import OrderedDict
from itertools import count

from .dependency import Dependency
from .release import Release
from .repositories import WareHouseRepo
from .root import RootDependency
from .node import Node


Dependency.repo = WareHouseRepo()
Release.repo = WareHouseRepo()


class Resolver:
    def __init__(self, deps):
        self.graph = OrderedDict((
            'root', Node.from_dependency(RootDependency(deps)),
        ))

    def apply(self, node):
        """Apply deps of passed node to graph
        """
        node.applied = True
        for dep in node.release.dependencies:
            if dep.normalized_name in self.graph:
                merged = self.merge_deps(self.graph[dep.normalized_name], dep)
                # conflict
                if not merged:
                    return dep
                # not needed, because merge_deps method merge deps in-place
                # self.graph[dep.normalized_name].dependency = dep
            else:
                self.graph[dep.normalized_name] = Node.from_dependency(dep)

    def merge_deps(self, node, dep):
        node.dependency.apply(dep)

        # if can't merge deps
        if not node.dependency.compat:
            return False

        # if choosen release already applied, but changed, we need to unapply it.
        if node.release not in node.dependency.releases:
            if node.applied:
                self.unapply(node=node)
                node.release = node.dependency.best_release
                node.layer = self.layer + 1

        return True

    def get_parents(self, node):
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

    def unapply(self, node):
        """Unapply dep from child deps
        """
        for other_node in self.graph.items():
            if node.dependency.normalized_name not in other_node.dependency.versions:
                continue
            other_node.dependency.unapply(node.dependency.normalized_name)
            self.unapply(node=other_node)

    def get_layers(self):
        """Iterate by graph layers
        """
        self.layer = 0
        for layer in count(start=1):
            child = [node for node in self.graph if node.layer == self.layer]
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
