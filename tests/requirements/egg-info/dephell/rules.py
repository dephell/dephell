# built-in
from collections import namedtuple


Rule = namedtuple('Rule', ['from_path', 'to_path', 'from_format', 'to_format'])

RULES = (
    Rule(
        from_path='requirements.in',
        to_path='requirements.txt',
        from_format='pip',
        to_format='piplock',
    ),
    Rule(
        from_path='requirements.txt',
        to_path='requirements.lock',
        from_format='pip',
        to_format='piplock',
    ),
    Rule(
        from_path='Pipfile',
        to_path='Pipfile.lock',
        from_format='pipfile',
        to_format='pipfilelock',
    ),
    Rule(
        from_path='pyproject.toml',
        to_path='pyproject.lock',
        from_format='poetry',
        to_format='poetrylock',
    ),
)

EXAMPLE_RULE = Rule(
    from_path='requirements.in',
    to_path='requirements.txt',
    from_format='pip',
    to_format='piplock',
)
