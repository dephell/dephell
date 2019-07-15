# external
from dephell_markers import Markers, OrMarker


class MarkerTracker:
    def __init__(self):
        self._markers = dict()

    @property
    def markers(self) -> Markers:
        if len(self._markers) == 1:
            return next(iter(self._markers.values()))
        container = Markers()
        markers = [m._marker for m in self._markers.values() if m._marker]
        container._marker = OrMarker(*markers)
        return container

    def apply(self, *, source, markers) -> 'MarkerTracker':
        if not markers:
            return self
        if type(source) is not str:
            source = source.name
        if source in self._markers:
            raise ValueError('marker for given source already added')
        if type(markers) is str:
            markers = Markers(markers)
        self._markers[source] = markers
        return self

    def merge(self, other: 'MarkerTracker') -> None:
        for source, marker in other._markers.items():
            self._markers[source] = marker

    def unapply(self, source) -> None:
        if type(source) is not str:
            source = source.name
        if source in self._markers:
            del self._markers[source]

    def __getattr__(self, name):
        if name not in dir(Markers):
            raise AttributeError(name)
        return getattr(self.markers, name)

    def __bool__(self) -> bool:
        return any(marker for marker in self._markers.values())

    def __str__(self) -> str:
        return str(self.markers)

    def __repr__(self):
        markers = map(repr, self._markers.values())
        return '{}({})'.format(type(self).__name__, ', '.join(markers))
