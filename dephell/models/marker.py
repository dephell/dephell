from typing import Union, Optional, Tuple

# external
from packaging import markers as packaging

from .range_specifier import RangeSpecifier


VARIABLES = dict(
    python_name=(
        'implementation_name',              # 'cpython'
        'platform_python_implementation',   # 'CPython'
    ),
    python_version=(
        'implementation_version',   # '3.5.2'
        'python_full_version',      # '3.5.2'
        'python_version',           # '3.5'
    ),
    platform_name=(
        'platform_system',      # 'Linux'
        'sys_platform',         # 'linux'
        'os_name',              # 'posix'
    ),
    platform_version=(
        'platform_release',     # '4.10.0-38-generic'
        'platform_version',     # '#42~16.04.1-Ubuntu SMP Tue Oct 10 16:32:20 UTC 2017'
        'platform_machine',     # 'x86_64'
    ),
    extra=('extra', ),
)


ALIASES = {
    'os.name': 'os_name',
    'sys.platform': 'sys_platform',
    'platform.version': 'platform_version',
    'platform.machine': 'platform_machine',
    'platform.python_implementation': 'platform_python_implementation',
    'python_implementation': 'python_implementation',
}


# https://github.com/pypa/packaging/blob/master/packaging/markers.py
class Markers(packaging.Marker):
    def __init__(self, markers: Union[list, str, 'Markers', packaging.Marker]):
        self._markers = self._parse(markers)

    def _parse(self, markers: Union[list, str, 'Markers', packaging.Marker]) -> list:
        if isinstance(markers, list):
            return markers
        if isinstance(markers, str):
            try:
                return packaging._coerce_parse_result(packaging.MARKER.parseString(markers))
            except packaging.ParseException as e:
                err_str = "invalid marker: {0!r}, parse error at {1!r}".format(
                    markers,
                    markers[e.loc:e.loc + 8],
                )
                raise packaging.InvalidMarker(err_str)
        return markers._markers

    @staticmethod
    def _get_marker(lhs: packaging.Node, rhs: packaging.Node, name: str) -> Tuple[str, Optional[str]]:
        if isinstance(lhs, packaging.Variable):
            marker_name = lhs.value
            marker_value = rhs.value
        else:
            marker_name = rhs.value
            marker_value = lhs.value
        if marker_name in ALIASES:
            marker_name = ALIASES[marker_name]
        if marker_name in VARIABLES[name]:
            return marker_name, marker_value
        return marker_name, None

    def _get_variable(self, name: str, markers=None) -> Optional[str]:
        if markers is None:
            markers = self._markers

        names = set()
        values = []
        for marker in markers:
            if isinstance(marker, tuple):
                lhs, op, rhs = marker
                marker_name, marker_value = self._get_marker(lhs=lhs, rhs=rhs, name=name)
                names.add(marker_name)
                if marker_value is not None:
                    values.append(op.value + marker_value)

        if values:
            # if all markers is `and` then this variable conditions required
            if 'or' not in markers:
                return ','.join(values)
            # if all markers is `or` and there is no any other vars
            if 'and' not in markers and len(names) == 1:
                if not any(type(m) is list for m in markers):
                    return ' || '.join(values)

    @property
    def python_version(self) -> Optional[RangeSpecifier]:
        value = self._get_variable('python_version')
        if value is not None:
            return RangeSpecifier(value)
