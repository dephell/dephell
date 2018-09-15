from .pip import from_pip, to_pip


LOADERS = dict(
    pip=from_pip,
)

DUMPERS = dict(
    pip=to_pip,
)
