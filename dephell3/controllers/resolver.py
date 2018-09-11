

class Resolver:
    def __init__(self, graph, mutator):
        self.graph = graph
        self.mutator = mutator

    def apply(self, parent):
        """
        Returns conflicting (incompatible) dependency
        """
        for new_dep in parent.dependencies:
            other_dep = self.graph.mapping.get(new_dep.normalized_name)
            if other_dep is None:
                # add new dep to graph
                self.graph.mapping.get[new_dep.normalized_name] = new_dep
                other_dep = new_dep
            else:
                # merge deps
                other_dep.merge(new_dep)
            # check
            if not other_dep.compat:
                return other_dep
        parent.applied = True

    def unapply(self, dep):
        if not dep.applied:
            return
        for child in dep.dependencies:
            # unapply current dependency for child
            child.unapply(dep.normalized_name)
            # unapply child because he is modified
            self.unapply(child)
        dep.applied = False

    def resolve(self) -> bool:
        while True:
            # get not applied deps
            deps = self.graph.get_leafs()
            # if we already build deps for all nodes in graph
            if not deps:
                return True

            for dep in deps:
                conflict = self.apply(dep)
                if conflict is not None:
                    # Dep can be partialy applied. Clean it.
                    self.unapply(dep)
                    self.graph.conflict = conflict
                    break
            else:
                # only if all deps applied
                continue

            # if we have conflict, try to mutate graph
            groups = self.mutator.mutate(self.graph)
            # if cannot mutate
            if groups is None:
                return False
            # apply mutation
            for group in groups:
                dep = self.graph.mapping[group.normalized_name]
                if dep.group.number != group.number:
                    self.unapply(dep)
                    dep.group = group
