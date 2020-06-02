from typing import Dict, Union

# external
from dephell_markers import Markers, OrMarker


class MarkerTracker:
    _markers: Dict[str, Markers]

    def __init__(self) -> None:
        self._markers = dict()

    @property
    def markers(self) -> Markers:
        container = Markers()

        if not self._markers:
            return container
        if len(self._markers) == 1:
            return next(iter(self._markers.values()))

        # Empty marker means "no markers should be applied, always match the dependency".
        for marker in self._markers.values():
            if not marker:
                return container

        # If no empty markers specified, merge all markers as `or`
        markers = [m._marker for m in self._markers.values()]
        container._marker = OrMarker(*markers)
        return container

    def apply(self, *, source, markers: Union[str, Markers]) -> 'MarkerTracker':
        if type(source) is not str:
            source = source.name
        if source in self._markers:
            raise ValueError('marker for given source already added')
        if type(markers) is str:
            markers = Markers(markers)
        self._markers[source] = markers  # type: ignore
        return self

    def merge(self, other: 'MarkerTracker') -> None:
        for source, marker in other._markers.items():
            self._markers[source] = marker

    def unapply(self, source) -> None:
        if type(source) is not str:
            source = source.name
        if source in self._markers:
            del self._markers[source]

    def __getattr__(self, name: str):
        if name not in dir(Markers):
            raise AttributeError(name)
        return getattr(self.markers, name)

    def __bool__(self) -> bool:
        return bool(self.markers)

    def __str__(self) -> str:
        return str(self.markers)

    def __repr__(self) -> str:
        markers = map(repr, self._markers.values())
        return '{}({})'.format(type(self).__name__, ', '.join(markers))
