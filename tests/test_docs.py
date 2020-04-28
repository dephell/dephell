# built-in
from pathlib import Path

# project
from dephell.config.scheme import SCHEME


def test_params_all_described():
    undocumented = {'and', 'auth', 'vars', 'command'}
    path = Path(__file__).parent.parent / 'docs' / 'params.md'
    content = path.read_text()
    for key in SCHEME:
        if key in undocumented:
            continue
        assert '`--' + key in content
