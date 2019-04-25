# built-in
from logging import getLogger
from typing import Optional

# external
from packaging.markers import Marker
from yaspin import yaspin

# app
from ..context_tools import nullcontext
from ..models import RootDependency
from .conflict import analyze_conflict


logger = getLogger('dephell.resolver')


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
                # if some of the dependencies cyclicaly depends on root
                # then ignore these deps
                continue
            else:
                # if dep is locked, but not used, let's just unlock it
                if other_dep.locked and not other_dep.used:
                    other_dep.unlock()
                # merge deps
                try:
                    other_dep += new_dep
                except TypeError:   # conflict happened
                    return other_dep
            # check
            if not other_dep.compat:
                return other_dep
        parent.applied = True

    def unapply(self, dep, *, force: bool = True, soft: bool = False) -> None:
        """
        force -- unapply deps that not applied yet
        soft -- do not mark dep as not applied.
        """
        if not force and not dep.applied:
            return
        # it must be before actual unapplying to avoid recursion on cyclic dependencies
        if not soft:
            dep.applied = False

        for child in dep.dependencies:
            child_name = child.name
            child = self.graph.get(child_name)
            if child is None:
                logger.debug('child not found', extra=dict(dep=dep.name, child=child_name))
                continue
            # unapply current dependency for child
            child.unapply(dep.name)
            # unapply child because he is modified
            self.unapply(child, force=False, soft=soft)

        if not soft and dep.locked:
            dep.unlock()

    def resolve(self, debug: bool = False, silent: bool = False, level: Optional[int] = None) -> bool:
        if silent:
            spinner = nullcontext(type('Mock', (), {}))
        else:
            spinner = yaspin(text='resolving...')

        with spinner as spinner:
            while True:
                resolved = self._resolve(debug=debug, silent=silent, level=level, spinner=spinner)
                if resolved is not None:
                    return resolved

    def _resolve(self, debug: bool, silent: bool, level: Optional[int], spinner) -> Optional[bool]:
        if silent:
            logger.debug('next iteration', extra=dict(
                layers=len(self.graph._layers),
                mutations=self.mutator.mutations,
            ))
        else:
            spinner.text = 'layers: {layers}, mutations: {mutations}'.format(
                layers=len(self.graph._layers),
                mutations=self.mutator.mutations,
            )
        # get not applied deps
        deps = self.graph.get_leafs(level=level)
        # if we already build deps for all nodes in graph
        if not deps:
            return True

        # check python version
        for dep in deps:
            if not dep.python_compat:
                self.graph.conflict = dep
                return False

        no_conflicts = self._apply_deps(deps, debug=debug)
        if no_conflicts:
            return None

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
            if dep.inherited_envs & envs:
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
            if not (dep.envs | dep.inherited_envs) & envs:
                continue
            self.apply(dep)

    def apply_markers(self, python) -> None:
        implementation = python.implementation
        if implementation == 'python':
            implementation = 'cpython'

        for dep in self.graph:
            if not dep.applied:
                continue
            if not dep.marker:
                continue

            fit = Marker(str(dep.marker)).evaluate(dict(
                python_version=str(python.version),
                implementation_name=implementation,
            ))
            if fit:
                continue

            self.unapply(dep, soft=True)
            dep.applied = False

    def _apply_deps(self, deps, debug: bool = False) -> bool:
        for dep in deps:
            conflict = self.apply(dep)
            if conflict is None:
                continue

            logger.debug('conflict', extra=dict(
                dep=conflict.name,
                constraint=conflict.constraint,
            ))
            self.graph.conflict = conflict.copy()

            if debug:
                print(analyze_conflict(
                    resolver=self,
                    suffix=str(self.mutator.mutations),
                ))

            # Dep can be partialy applied. Clean it.
            self.unapply(dep)
            return False

        # only if all deps applied
        return True
