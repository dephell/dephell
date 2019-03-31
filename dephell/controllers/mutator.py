# built-in
from typing import Optional

# app
from ..utils import lazy_product


class Mutator:
    def __init__(self):
        self._snapshots = set()

    def mutate(self, graph) -> Optional[tuple]:
        """Get graph with conflict and mutate one dependency.

        Mutation changes group for one from dependencies
        from parents of conflicting dependency.
        """
        parents = graph.get_parents(graph.conflict)
        for groups in self.get_mutations(parents.values()):
            if self.check(groups):
                self.remember(groups)
                return groups
        return None  # mypy wants it

    def get_mutations(self, deps):
        all_groups = []
        for dep in deps:
            all_groups.append(dep.groups)
        for groups in lazy_product(*all_groups):
            yield groups

    @staticmethod
    def _make_snapshot(groups) -> tuple:
        snapshot = sorted(group.name + '|' + str(group.number) for group in groups)
        return tuple(snapshot)

    def check(self, groups) -> bool:
        for group in groups:
            if group.empty:
                return False
        return self._make_snapshot(groups) not in self._snapshots

    def remember(self, groups):
        self._snapshots.add(self._make_snapshot(groups))

    @property
    def mutations(self) -> int:
        return len(self._snapshots)

    def __repr__(self) -> str:
        return '{name}(mutations={mutations})'.format(
            name=type(self).__name__,
            mutations=self.mutations,
        )
