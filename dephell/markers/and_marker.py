# built-in
from typing import Optional, Set, Tuple

# app
from .operation import Operation


class AndMarker(Operation):
    op = 'and'
    sep = ','

    def __str__(self):
        # braces is redundant for `and`
        return super().__str__()[1:-1]

    def _get_values(self, name: str) -> Optional[Set[Tuple[str, str]]]:
        values = set()  # type: Set[Tuple[str, str]]
        for node in self.nodes:
            if isinstance(node, Operation):
                subvalues = node._get_values(name)
                if subvalues is not None:
                    values.union(subvalues)
            elif node.variable == name:
                values.add((node.operator, node.value))
        if values:
            return values
        return None
