# isort skips this file, but `flake8-isort` can't read pyproject.toml
import django               # isort:skip
from flake8 import api      # isort:skip
from yaml.api import lol    # isort:skip

__all__ = ['django', 'api', 'lol', 'pytest']

1 / 0

import pytest  # noqa: E402
