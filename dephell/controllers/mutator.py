# built-in
from logging import getLogger
from typing import Optional, Tuple

import attr

# app
from ..config import config
from ..utils import lazy_product


logger = getLogger('dephell.controllers')


@attr.s()
class Mutator:
    limit = attr.ib(type=int, factory=lambda: config['mutations'])
    mutations = attr.ib(type=int, default=0, init=False)
    _snapshots = attr.ib(type=set, factory=set, repr=False, init=False)

    def mutate(self, graph) -> Optional[tuple]:
        """Get graph with conflict and mutate one dependency.

        Mutation changes group for one from dependencies
        from parents of conflicting dependency.
        """
        if self.mutations >= self.limit:
            logger.warning('mutations limit reached', extra=dict(limit=self.limit))
            return None

        parents = graph.get_parents(graph.conflict)
        for groups in self.get_mutations(parents.values()):
            if self.check(groups):
                self.remember(groups)
                self.mutations += 1
                return groups
        return None  # mypy wants it

    def get_mutations(self, deps):
        all_groups = []
        for dep in deps:
            all_groups.append(dep.groups)
        for groups in lazy_product(*all_groups):
            yield groups

    @staticmethod
    def _make_snapshot(groups) -> Tuple[str]:
        snapshot = sorted(group.name + '|' + str(group.number) for group in groups)
        return tuple(snapshot)

    def check(self, groups) -> bool:
        for group in groups:
            if group.empty:
                return False
        return self._make_snapshot(groups) not in self._snapshots

    def remember(self, groups) -> None:
        self._snapshots.add(self._make_snapshot(groups))

    def __repr__(self) -> str:
        return '{name}(mutations={mutations})'.format(
            name=type(self).__name__,
            mutations=self.mutations,
        )
