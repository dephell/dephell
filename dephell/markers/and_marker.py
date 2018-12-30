from typing import Optional
from .operation import Operation


class AndMarker(Operation):
    op = 'and'
    sep = ','

    def __str__(self):
        # braces is redundant for `and`
        return super().__str__()[1:-1]

    def get_string(self, name: str) -> Optional[str]:
        values = set()
        for node in self.nodes:
            if isinstance(node, Operation):
                value = node.get_string(name)
                if value is not None:
                    values.add(value)
            elif node.variable == name:
                values.add(node.value)
        if values:
            return self.sep.join(sorted(values))
        return None
