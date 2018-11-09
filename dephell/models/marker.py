# external
from packaging.markers import MARKER, Marker, _coerce_parse_result


# https://github.com/pypa/packaging/blob/master/packaging/markers.py
class Markers(Marker):
    def __init__(self, markers):
        self._markers = self.parse()

    def _parse(self, markers):
        if isinstance(markers, list):
            return markers
        if isinstance(markers, str):
            return _coerce_parse_result(MARKER.parseString(markers))
        return markers._markers
