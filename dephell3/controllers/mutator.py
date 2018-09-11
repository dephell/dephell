from itertools import product


class Mutator:
    def __init__(self):
        ...

    def mutate(self, graph):
        """Get graph with conflict and mutate one dependency.

        Mutation changes group for one from dependencies
        from parents of conflicting dependency.
        """
        parents = graph.get_parents(graph.conflict)
        for deps in self.get_mutations(parents):
            if self.check(deps):
                self.remember(deps)
                return True
        return False

    def get_mutations(self, deps):
        all_groups = tuple(dep.groups for dep in deps)
        for groups in product(*all_groups):
            for dep, group in zip(deps, groups):
                dep.group = group
            yield deps

    def check(self, deps):
        ...

    def remember(self, deps):
        ...
