from logging import getLogger


logger = getLogger(__name__)


class Graph:
    def __init__(self, root):
        self.root = root
        self.reset()

    def reset(self):
        self.mapping = {self.root.name: self.root}
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
        for children in dep.dependencies:
            if graph and children.normalized_name not in self.mapping:
                continue
            if children.normalized_name in result:
                logger.warning('Recursive dependency: {}'.format(children))
            else:
                result[children.normalized_name] = children
            if layers != 0:
                result.update(self.get_child(children, layers=layers))
        return result

    def get_parents(self, dep, *, layers=None) -> dict:
        parents = dict()
        for parent in self.mapping.values():
            if dep.normalized_name in self.get_child(parent, layers=layers):
                parents[dep.normalized_name] = dep
        return parents
