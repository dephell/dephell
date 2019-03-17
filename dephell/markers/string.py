# built-in
from typing import Optional

# external
from packaging.markers import Op, Value

# app
from .base import BaseMarker


class StringMarker(BaseMarker):

    def get_string(self, name: str) -> Optional[str]:
        if name != self.variable:
            return None
        if self.operator != '==':
            return None
        return self.value

    def get_version(self, name: str) -> Optional[str]:
        return None

    def __str__(self):
        if isinstance(self.lhs, Value):
            template = '"{lhs}" {op} {rhs}'
        else:
            template = '{lhs} {op} "{rhs}"'
        return template.format(
            lhs=self.lhs.value,
            op=self.op.value,
            rhs=self.rhs.value,
        )

    def __add__(self, other):
        if self.lhs.value != other.lhs.value:
            return NotImplemented
        if self.rhs.value != other.rhs.value:
            return NotImplemented

        if self.op.value == other.op.value:
            return self
        operations = {self.op.value, other.op.value}
        if operations in ({'>=', '=='}, {'<=', '=='}, {'>=', '<='}):
            return type(self)(
                lhs=self.lhs,
                op=Op(value='=='),
                rhs=self.rhs,
            )

        return NotImplemented
