from pathlib import Path
from typing import Any, Dict, Optional

# external
from jinja2 import Environment, PackageLoader


env = Environment(loader=PackageLoader('dephell', 'templates'))
KNOWN_SECTIONS = (
    ('test', 'tests'),
    ('tests', 'tests'),
    ('testing', 'tests'),
    ('unittest', 'tests'),
    ('pytest', 'tests'),

    ('linter', 'lint'),
    ('linters', 'lint'),
    ('flake', 'lint'),
    ('pylint', 'lint'),
    ('flake8', 'lint'),

    ('types', 'typing'),
    ('typing', 'typing'),
    ('mypy', 'typing'),

    ('isort', 'isort'),
    ('sort', 'isort'),
)


def make_contributing(config: Dict[str, Dict[str, Any]], project_path: Path) -> Optional[str]:
    template = env.get_template('contributing.md.j2')
    envs = dict()
    for name, category in KNOWN_SECTIONS:
        if name not in config:
            continue
        envs[category] = name
    content = template.render(project_name=project_path.name, envs=envs)
    while '\n\n\n' in content:
        content = content.replace('\n\n\n', '\n\n')
    return content
