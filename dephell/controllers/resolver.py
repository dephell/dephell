from logging import getLogger
from .conflict import analize_conflict

logger = getLogger('dephell.resolver')


class Resolver:
    def __init__(self, graph, mutator):
        self.graph = graph
        self.mutator = mutator

    def apply(self, parent):
        """
        Returns conflicting (incompatible) dependency
        """
        for new_dep in parent.dependencies:
            other_dep = self.graph.get(new_dep.name)
            if other_dep is None:
                # add new dep to graph
                other_dep = new_dep.copy()
                self.graph.add(other_dep)
            else:
                # merge deps
                other_dep.merge(new_dep)
            # check
            if not other_dep.compat:
                return other_dep
        parent.applied = True

    def unapply(self, dep, *, force=True):
        if not force and not dep.applied:
            return
        for child in dep.dependencies:
            child = self.graph.get(child.name)
            if child is None:
                logger.warning('child not found')
                continue
            # unapply current dependency for child
            child.unapply(dep.name)
            # unapply child because he is modified
            self.unapply(child, force=False)
        dep.applied = False

    def resolve(self, debug=False) -> bool:
        while True:
            # get not applied deps
            deps = self.graph.get_leafs()
            # if we already build deps for all nodes in graph
            if not deps:
                return True

            for dep in deps:
                conflict = self.apply(dep)
                if conflict is not None:
                    logger.debug('conflict {}{}'.format(conflict.name, conflict.constraint))
                    self.graph.conflict = conflict.copy()

                    if debug:
                        print(analize_conflict(
                            resolver=self,
                            suffix=str(self.mutator.mutations),
                        ))

                    # Dep can be partialy applied. Clean it.
                    self.unapply(dep)
                    break
            else:
                # only if all deps applied
                continue

            # if we have conflict, try to mutate graph
            groups = self.mutator.mutate(self.graph)
            # if cannot mutate
            if groups is None:
                return False
            self.graph.conflict = None
            # apply mutation
            for group in groups:
                dep = self.graph.get(group.name)
                if dep.group.number != group.number:
                    logger.debug('mutated {} to {}'.format(str(dep.group), str(group)))
                    self.unapply(dep)
                    dep.group = group
