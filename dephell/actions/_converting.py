# built-in
from logging import getLogger
from pathlib import Path

# app
from ..config import Config
from ..converters import CONVERTERS


logger = getLogger('dephell.actions')


def attach_deps(*, resolver, config: Config, merge: bool = True) -> bool:
    if 'and' not in config:
        return True

    # attach
    for source in config['and']:
        logger.debug('attach dependencies...', extra=dict(
            format=source['format'],
            path=source['path'],
        ))
        loader = CONVERTERS[source['format']]
        root = loader.load(path=source['path'])

        # fix name for new root to avoid conflicts
        names = {other.name for other in resolver.graph.get_layer(0)}
        if root.name in names:
            if source['format'] not in names:
                root.name = source['format']
            else:
                name = Path(source['path']).name
                if name not in names:
                    root.name = name
            # TODO: generate random name
            ...

        resolver.graph.add(root)

    if not merge:
        return True

    # merge (without full graph building)
    logger.debug('merging...')
    resolved = resolver.resolve(level=1, silent=config['silent'])
    if not resolved:
        return False
    logger.debug('merged')

    return True
