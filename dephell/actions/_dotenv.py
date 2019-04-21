# built-in
import shlex
from codecs import decode
from pathlib import Path
from string import Template
from typing import Dict


def read_dotenv(path: Path, env_vars: Dict[str, str] = None) -> Dict[str, str]:
    if env_vars is None:
        env_vars = dict()
    else:
        env_vars = env_vars.copy()

    if path.is_dir():
        path = path / '.env'
    if not path.exists():
        return env_vars

    with path.open('r', encoding='utf-8') as stream:
        for line in stream:
            line = line.strip()
            if not line or line[0] == '#':
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
            value = decode(value, 'unicode-escape')
            if '$' in value:
                value = value.replace(r'\$', '$$')  # escaping
                value = Template(value).safe_substitute(env_vars)

            env_vars[key] = value

    return env_vars
