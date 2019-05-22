# built-in
import re
from logging import getLogger

# external
from jinja2 import Environment, PackageLoader


logger = getLogger('dephell')
env = Environment(
    loader=PackageLoader('dephell', 'templates'),
)


REPLACEMENTS = (
    ('</div>', '\n\n'),
    ('</ul>', '\n\n'),
    ('</ol>', '\n\n'),

    ('</li>', '\n'),
    ('</p>', '\n'),

    ('<ul>', '\n'),
    ('<ol>', '\n'),
    ('<li>', ' + '),
    ('<hr/>', '\n' + '—' * 80 + '\n'),
)
REX_BEGINNING = re.compile(r'(\n[ \t]+)')


# https://github.com/dephell/dephell/issues/11
def html2text(text: str) -> str:
    text = REX_BEGINNING.sub('', text)
    for tag, char in REPLACEMENTS:
        text = text.replace(tag, char)
    for tag, _ in REPLACEMENTS:
        text = text.replace(tag.replace('/', ''), '')
    while '\n\n\n' in text:
        text = text.replace('\n\n\n', '\n\n')
    return text.strip() + '\n'


def analyze_conflict(resolver, suffix: str = '') -> str:
    try:
        resolver.graph.draw(suffix=suffix)
    except ImportError as e:
        logger.warning(e.args[0])

    conflict = resolver.graph.conflict
    if conflict is None:
        templates = ('state.html.j2', )
    elif not resolver.graph.conflict.python_compat:
        templates = ('python.html.j2', )
    else:
        templates = ('conflict.html.j2', 'state.html.j2')

    content = []
    for template_name in templates:
        template = env.get_template(template_name)
        content.append(template.render(
            conflict=resolver.graph.conflict,
            graph=resolver.graph,
            mutator=resolver.mutator,
        ))
    return html2text('\n\n'.join(content))
