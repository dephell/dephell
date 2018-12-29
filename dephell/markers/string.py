from packaging.markers import Value, Op

from .base import BaseMarker


class StringMarker(BaseMarker):
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
