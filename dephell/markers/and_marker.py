from typing import Optional, Set
from .operation import Operation


class AndMarker(Operation):
    op = 'and'
    sep = ','

    def __str__(self):
        # braces is redundant for `and`
        return super().__str__()[1:-1]

    def _get_values(self, name: str) -> Optional[Set[str]]:
        values = set()
        for node in self.nodes:
            if isinstance(node, Operation):
                value = node.get_string(name)
                if value is not None:
                    values.add(value)
            elif node.variable == name:
                values.add(node.value)
        if values:
            return values
        return None
