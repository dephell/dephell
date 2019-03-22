
from contextlib import suppress
from logging import getLogger
from typing import Optional


from tqdm import tqdm

# app
from ..config import config
from .conflict import analize_conflict


logger = getLogger('dephell.resolver')


class _Progress(tqdm):
    @classmethod
    def _decr_instances(cls, instance):
        with suppress(RuntimeError):
            return super()._decr_instances(instance)


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
                try:
                    other_dep += new_dep
                except TypeError:   # conflict happened
                    return other_dep
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

    def resolve(self, debug: bool = False, level: Optional[int] = None) -> bool:
        if not config['silent']:
            layers_bar = _Progress(
                total=10 ** 10,
                bar_format='{n:>7} layers   [{elapsed} elapsed]',
                position=1,
                leave=False,
            )

        while True:
            if not config['silent']:
                layers_bar.update()
            # get not applied deps
            deps = self.graph.get_leafs(level=level)
            # if we already build deps for all nodes in graph
            if not deps:
                if not config['silent']:
                    del layers_bar
                    print('\r')
                return True

            # check python version
            for dep in deps:
                if not dep.python_compat:
                    self.graph.conflict = dep
                    return False

            no_conflicts = self._apply_deps(deps, debug=debug)
            if no_conflicts:
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
                    logger.debug('mutated {group_from} to {group_to}', extra=dict(
                        group_from=str(dep.group),
                        group_to=str(group),
                    ))
                    self.unapply(dep)
                    dep.group = group

    def _apply_deps(self, deps, debug: bool = False) -> bool:
        if not config['silent']:
            packages_bar = _Progress(
                total=len(deps),
                bar_format='{n:>3}/{total:>3} packages [{elapsed} elapsed]',
                position=2,
                leave=False,
            )

        for dep in deps:
            if not config['silent']:
                packages_bar.update()
            conflict = self.apply(dep)
            if conflict is None:
                continue

            logger.debug('conflict {name}{constraint}', extra=dict(
                name=conflict.name,
                constraint=conflict.constraint,
            ))
            self.graph.conflict = conflict.copy()

            if debug:
                print(analize_conflict(
                    resolver=self,
                    suffix=str(self.mutator.mutations),
                ))

            # Dep can be partialy applied. Clean it.
            self.unapply(dep)
            return False

        # only if all deps applied
        return True
