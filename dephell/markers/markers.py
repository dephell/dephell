from typing import Union, Optional

# external
from packaging import markers as packaging
from packaging.markers import Variable

from ..models.range_specifier import RangeSpecifier
from .and_marker import AndMarker
from .or_marker import OrMarker
from .string import StringMarker
from .version import VersionMarker
from .constants import STRING_VARIABLES, VERSION_VARIABLES


class Markers:
    def __init__(self, markers: Union[list, str, 'Markers', packaging.Marker]):
        markers = self._parse(markers)
        if isinstance(markers, list):
            self._marker = self._convert(markers)
        else:
            self._marker = markers

    @staticmethod
    def _parse(markers: Union[list, str, 'Markers', packaging.Marker]):
        if isinstance(markers, list):
            return markers

        if isinstance(markers, str):
            # https://github.com/pypa/packaging/blob/master/packaging/markers.py
            try:
                return packaging._coerce_parse_result(packaging.MARKER.parseString(markers))
            except packaging.ParseException as e:
                err_str = "invalid marker: {0!r}, parse error at {1!r}".format(
                    markers,
                    markers[e.loc:e.loc + 8],
                )
                raise packaging.InvalidMarker(err_str)

        if hasattr(markers, '_markers'):
            return markers._markers

        if hasattr(markers, '_marker'):
            return markers._marker

        raise ValueError('invalid marker')

    @classmethod
    def _convert(cls, markers: list):
        groups = [[]]  # list of nodes and operations between them
        for marker in markers:
            # single marker
            if isinstance(marker, tuple):
                lhs, op, rhs = marker
                var = lhs.value if isinstance(lhs, Variable) else rhs.value
                if var in STRING_VARIABLES:
                    marker_cls = StringMarker
                elif var in VERSION_VARIABLES:
                    if op.value in {'in', 'not in'}:
                        msg = 'Unsupported operation for version marker {}: {}'
                        raise ValueError(msg.format(var, op.value))
                    marker_cls = VersionMarker
                else:
                    raise LookupError('unknown marker: {}'.format(var))
                groups[-1].append(marker_cls(lhs=lhs, op=op, rhs=rhs))
                continue

            # sub-collection
            if isinstance(marker, list):
                groups[-1].append(cls._convert(marker))
                continue

            # operation
            if isinstance(marker, str):
                if marker == 'or':
                    groups.append([])
                continue

            raise LookupError('invalid node type')

        new_groups = []
        for group in groups:
            if len(group) == 1:
                new_groups.append(group[0])
            elif len(group) > 1:
                new_groups.append(AndMarker(*group))

        if len(new_groups) == 1:
            return new_groups[0]
        return OrMarker(*new_groups)

    def get_string(self, name: str) -> Optional[str]:
        return self._marker.get_string(name=name)

    def get_version(self, name: str) -> Optional[str]:
        return self._marker.get_version(name=name)

    def add(self, *, name: str, value, operator: str = '=='):
        if operator in {'in', 'not in'}:
            msg = 'Unsupported operation: {}'
            raise ValueError(msg.format(operator))

        if name in STRING_VARIABLES:
            marker_cls = StringMarker
        elif name in VERSION_VARIABLES:
            marker_cls = VersionMarker
        marker = marker_cls(
            lhs=packaging.Variable(name),
            op=packaging.Op(operator),
            rhs=packaging.Value(value),
        )

        if isinstance(self._marker, AndMarker):
            self._marker.nodes.append(marker)
            return marker

        self._marker = AndMarker(marker, self._marker)
        return marker

    @property
    def python_version(self) -> Optional[RangeSpecifier]:
        value = self.get_version('python_version')
        if value is not None:
            return RangeSpecifier(value)

    @property
    def extra(self) -> Optional[str]:
        return self.get_string('extra')

    def __repr__(self):
        return '{}({!r})'.format(type(self).__name__, self._marker)

    def __str__(self):
        return str(self._marker).strip('()')
