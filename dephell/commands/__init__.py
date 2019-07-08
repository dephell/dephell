# app
from .discover import COMMANDS


__all__ = ['COMMANDS']

# allow to import commands
locals().update({c.__name__: c for c in COMMANDS.values()})
__all__.extend(COMMANDS)
