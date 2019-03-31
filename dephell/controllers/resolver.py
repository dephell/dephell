# built-in
from contextlib import suppress
from logging import getLogger
from typing import Optional

# external
from tqdm import tqdm

# app
from ..config import config
from .conflict import analize_conflict
from ..models import RootDependency


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
            elif isinstance(other_dep, RootDependency):
                # if some of the dependencies cyclicaly dependes on root
                # then ignore these deps
                continue
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

    def unapply(self, dep, *, force=True, soft=False):
        """
        force -- unapply deps that not applied yet
        soft -- do not mark dep as not applied.
        """
        if not force and not dep.applied:
            return
        for child in dep.dependencies:
            child = self.graph.get(child.name)
            if child is None:
                logger.warning('child not found', extra=dict(dep=dep.name))
                continue
            # unapply current dependency for child
            child.unapply(dep.name)
            # unapply child because he is modified
            self.unapply(child, force=False, soft=soft)
        if not soft:
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
            if config['silent']:
                logger.debug('next layer', extra=dict(
                    layers=len(self.graph._layers),
                ))
            else:
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
                    logger.debug('mutated', extra=dict(
                        group_from=str(dep.group),
                        group_to=str(group),
                    ))
                    self.unapply(dep)
                    dep.group = group

    def apply_envs(self, envs: set) -> None:
        layer = self.graph.get_layer(1)

        # Unapply deps that we don't need
        for dep in layer:
            if not dep.applied:
                continue
            if dep.envs & envs:
                continue
            # without `soft=True` all deps of this dep will be marked as unapplied
            # and ignored in Requirement.from_graph.
            # It's bad behavior because deps of this dep can be required for other
            # deps that won't be unapplied.
            self.unapply(dep, soft=True)
            dep.applied = False

        # Some child deps can be unapplied from other child deps, but we need them.
        # For example, if we need A, but don't need B, and A and B depends on C,
        # then C will be unapplied from B. Let's retun B in the graph by apllying A.
        for dep in layer:
            if not dep.applied:
                continue
            if not dep.envs & envs:
                continue
            self.apply(dep)

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

            logger.debug('conflict', extra=dict(
                dep=conflict.name,
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
