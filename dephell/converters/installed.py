
# built-in
import sys
from pathlib import Path

# app
from .egginfo import EggInfoConverter


class InstalledConverter:
    lock = True

    def load(self):
        for path in sys.path:
            path = Path(path)
            for info_path in path.glob('*.egg-info'):
                subroot = EggInfoConverter.load(info_path) # noQA
                ...
