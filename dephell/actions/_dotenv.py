import shlex
from pathlib import Path
from string import Template
from typing import Dict


def read_dotenv(path: Path) -> Dict[str, str]:
    if path.is_dir():
        path = path / '.env'
    if not path.exists():
        return dict()
    vars = dict()

    with path.open('r', encoding='utf-8') as stream:
        for line in stream:
            line = line.strip()
            if not line or line[0] in ('//', '#'):
                continue
            key, value = line.split('=', 1)

            # clean key
            key = key.strip()
            if key.startswith('export '):
                key = key.replace('export ', '', 1)
                key = key.strip()
            if key[0] == '$':
                key = key[1:]

            # clean and substitute value
            value = ' '.join(shlex.split(value, comments=True))
            if '$' in value:
                value = Template(value).safe_substitute(vars)

            vars[key] = value

    return vars
