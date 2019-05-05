# built-in
from logging import getLogger
from typing import Iterable, Iterator, Optional, Sequence, Set, Tuple

# external
import attr

# app
from ..config import config
from ..models import Dependency, Group, RootDependency
from ..utils import lazy_product
from .dependency import DependencyMaker
from .graph import Graph


logger = getLogger('dephell.controllers')


@attr.s()
class Mutator:
    limit = attr.ib(type=int, factory=lambda: config['mutations'])
    mutations = attr.ib(type=int, default=0, init=False)
    _snapshots = attr.ib(type=Set[Tuple[str, ...]], factory=set, repr=False, init=False)

    def mutate(self, graph: Graph) -> Optional[Tuple[Group, ...]]:
        """Get graph with conflict and mutate one dependency.

        Mutation changes group for one from dependencies
        from parents of conflicting dependency.
        """
        if self.mutations >= self.limit:
            logger.warning('mutations limit reached', extra=dict(limit=self.limit))
            return None

        parents = tuple(graph.get_parents(graph.conflict).values())
        checker = (
            self._check_in_conflict,
            self._check_in_subgraph,
            self._check_not_empty,
            # self._check_soft,
        )
        for check in checker:
            for groups in self.get_mutations(deps=parents):
                if check(groups=groups, deps=parents, conflict=graph.conflict):
                    self.remember(groups)
                    self.mutations += 1
                    return groups
        return None  # mypy wants it

    def get_mutations(self, deps: Iterable[Dependency]) -> Iterator[Tuple[Group, ...]]:
        all_groups = []
        for dep in deps:
            all_groups.append(dep.groups)
        for groups in lazy_product(*all_groups):
            yield groups

    @staticmethod
    def _make_snapshot(groups: Iterable[Group]) -> Tuple[str, ...]:
        snapshot = sorted(group.name + '|' + str(group.number) for group in groups)
        return tuple(snapshot)

    def _check_soft(self, groups: Sequence[Group], deps: Sequence[Dependency],
                    conflict: Dependency) -> bool:
        return self._make_snapshot(groups) not in self._snapshots

    def _check_not_empty(self, groups: Sequence[Group], deps: Sequence[Dependency],
                         conflict: Dependency) -> bool:
        for group in groups:
            if group.empty:
                return False
        return self._check_soft(groups=groups, deps=deps, conflict=conflict)

    def _check_in_subgraph(self, groups: Sequence[Group], deps: Sequence[Dependency],
                           conflict: Dependency) -> bool:
        if not self._check_not_empty(groups=groups, deps=deps, conflict=conflict):
            return False
        # any new group has to change state of the subgraph
        state = {dep.name: dict(dep.constraint.specs) for dep in deps if not isinstance(dep, RootDependency)}
        state[conflict.name] = dict(conflict.constraint.specs)
        for group, dep in zip(groups, deps):
            for subdep in group.dependencies:
                if isinstance(subdep, Dependency):
                    if subdep.name not in state:
                        continue
                    if dep.name not in state[subdep.name]:
                        return True
                    if state[subdep.name][dep.name] != str(subdep.constraint):
                        return True
                    continue

                for subdep in DependencyMaker.from_requirement(dep, subdep):
                    if subdep.name not in state:
                        continue
                    if dep.name not in state[subdep.name]:
                        return True
                    if state[subdep.name][dep.name] != str(subdep.constraint):
                        return True
        return False

    def _check_in_conflict(self, groups: Sequence[Group], deps: Sequence[Dependency],
                           conflict: Dependency) -> bool:
        if not self._check_not_empty(groups=groups, deps=deps, conflict=conflict):
            return False
        state = {dep.name: dict(dep.constraint.specs) for dep in deps if not isinstance(dep, RootDependency)}
        state[conflict.name] = dict(conflict.constraint.specs)
        for group, dep in zip(groups, deps):
            for subdep in group.dependencies:
                if isinstance(subdep, Dependency):
                    if subdep.name == conflict.name:
                        return True
                    continue
                for subdep in DependencyMaker.from_requirement(dep, subdep):
                    if subdep.name == conflict.name:
                        return True
        return False

    def remember(self, groups: Iterable[Group]) -> None:
        self._snapshots.add(self._make_snapshot(groups))
