from itertools import product


class Mutator:
    def __init__(self):
        self._snapshots = set()

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

    @staticmethod
    def _make_snapshot(groups) -> tuple:
        snapshot = sorted(group.normalized_name + str(group.number) for group in groups)
        return tuple(snapshot)

    def check(self, groups):
        return self._make_snapshot(groups) in self._snapshots

    def remember(self, groups):
        self._snapshots.add(self._make_snapshot(groups))
