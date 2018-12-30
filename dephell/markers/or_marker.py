from typing import Optional, Set
from .operation import Operation


class OrMarker(Operation):
    op = 'or'
    sep = ' || '

    def _get_values(self, name: str) -> Optional[Set[str]]:
        values = set()
        for node in self.nodes:
            if isinstance(node, Operation):
                value = node.get_string(name)
                if value is None:
                    return None
                else:
                    values.add(value)
            elif node.variable == name:
                values.add(node.value)
            else:
                return None
        if values:
            return values
        return None
