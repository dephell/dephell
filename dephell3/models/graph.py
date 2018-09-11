from logging import getLogger


logger = getLogger(__name__)


class Graph:
    def __init__(self, root):
        self.mapping = {root.name: root}
        self.conflict = None

    def get_leafs(self):
        for dep in self.mapping.values():
            if dep.locked:
                yield dep

    def get_child(self, dep, *, graph=True, layers=None) -> dict:
        if not dep.locked:
            return dict()
        if layers is not None:
            layers -= 1

        result = dict()
        for subdep in dep.dependencies:
            if graph and subdep.name not in self.mapping:
                continue
            if subdep.name in result:
                logger.warning('Recursive dependency: {}'.format(subdep))
            else:
                result[subdep.name] = subdep
            if layers != 0:
                result.update(self.get_child(subdep, layers=layers))
        return result

    def get_parents(self, dep, *, layers=None) -> dict:
        ...
