# built-in
from typing import Optional, Set, Tuple

# app
from .operation import Operation


class OrMarker(Operation):
    op = 'or'
    sep = ' || '

    def _get_values(self, name: str) -> Optional[Set[Tuple[str, str]]]:
        values = set()  # type: Set[Tuple[str, str]]
        for node in self.nodes:
            if isinstance(node, Operation):
                subvalues = node._get_values(name)
                if subvalues is None:
                    return None
                else:
                    values.union(subvalues)
            elif node.variable == name:
                values.add((node.operator, node.value))
            else:
                return None
        if values:
            return values
        return None
