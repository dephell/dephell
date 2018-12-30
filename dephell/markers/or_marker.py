from typing import Optional
from .operation import Operation


class OrMarker(Operation):
    op = 'or'
    sep = ' || '

    def get_string(self, name: str) -> Optional[str]:
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
            return self.sep.join(sorted(values))
        return None
