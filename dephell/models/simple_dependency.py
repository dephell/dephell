from typing import Optional, FrozenSet

import attr
from packaging.requirements import Requirement


@attr.s(slots=True, frozen=True)
class SimpleDependency:
    """Simplified dependency model

    Compatible with packaging.requirements.Requirement.
    Used in repos for release dependencies to avoid recursion.
    """
    name = attr.ib(type=str)
    specifier = attr.ib(type=str, default='*')

    url = attr.ib(type=Optional[str], default=None)
    marker = attr.ib(type=Optional[str], default=None)
    extras = attr.ib(type=FrozenSet[str], factory=frozenset)

    @classmethod
    def from_string(cls, text: str) -> 'SimpleDependency':
        req = Requirement(text)
        return cls(
            name=req.name,
            specifier=req.specifier,

            url=req.url,
            marker=req.marker,
            extras=req.extras,
        )
