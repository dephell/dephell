from itertools import product


class Mutator:
    def __init__(self):
        ...

    def mutate(self, graph) -> tuple:
        """Get graph with conflict and mutate one dependency.

        Mutation changes group for one from dependencies
        from parents of conflicting dependency.
        """
        parents = graph.get_parents(graph.conflict)
        for groups in self.get_mutations(parents):
            if self.check(groups):
                self.remember(groups)
                return groups

    def get_mutations(self, deps):
        all_groups = []
        for dep in deps:
            all_groups.append(tuple(group for group in dep.groups if not group.empty))
        for groups in product(*all_groups):
            yield groups

    def check(self, groups):
        ...

    def remember(self, groups):
        ...
