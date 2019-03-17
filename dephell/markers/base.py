import attr
from ..utils import cached_property
from packaging.markers import Variable, Value

from .constants import ALIASES


@attr.s()
class BaseMarker:
    lhs = attr.ib()
    op = attr.ib()
    rhs = attr.ib()

    def __attrs_post_init__(self):
        # change alias to good value
        if isinstance(self.lhs, Variable):
            value = ALIASES.get(self.lhs.value)
            if value is not None:
                self.lhs = Variable(value=value)
        if isinstance(self.rhs, Variable):
            value = ALIASES.get(self.rhs.value)
            if value is not None:
                self.rhs = Variable(value=value)

    @cached_property
    def variable(self) -> str:
        if isinstance(self.lhs, Variable):
            return self.lhs.value
        return self.rhs.value

    @property
    def operator(self) -> str:
        return self.op.value

    @cached_property
    def value(self) -> str:
        if isinstance(self.rhs, Value):
            return self.rhs.value
        return self.lhs.value
