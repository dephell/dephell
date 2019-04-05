"""Actions are functions that used only in commands
"""
from ._python import get_python
from ._venv import get_venv


__all__ = [
    'get_python',
    'get_venv',
]
