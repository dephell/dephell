# built-in
from contextlib import suppress
from logging import getLogger

# external
from tqdm import tqdm

# app
from ..exceptions import MergeError
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
                    other_dep.merge(new_dep)
                except MergeError:
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

    def resolve(self, debug: bool=False, progress: bool=False, level=None) -> bool:
        if progress:
            layers_bar = _Progress(
                total=10 ** 10,
                bar_format='{n:>7} layers   [{elapsed} elapsed]',
                position=1,
                leave=False,
            )

        while True:
            if progress:
                layers_bar.update()
            # get not applied deps
            deps = self.graph.get_leafs(level=level)
            # if we already build deps for all nodes in graph
            if not deps:
                if progress:
                    del layers_bar
                    print('\r')
                return True

            no_conflicts = self._apply_deps(deps, debug=debug, progress=progress)
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
                    logger.debug('mutated {} to {}'.format(str(dep.group), str(group)))
                    self.unapply(dep)
                    dep.group = group

    def _apply_deps(self, deps, progress=False, debug=False):
        if progress:
            packages_bar = _Progress(
                total=len(deps),
                bar_format='{n:>3}/{total:>3} packages [{elapsed} elapsed]',
                position=2,
                leave=False,
            )

        for dep in deps:
            if progress:
                packages_bar.update()
            conflict = self.apply(dep)
            if conflict is None:
                continue

            logger.debug('conflict {}{}'.format(conflict.name, conflict.constraint))
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
