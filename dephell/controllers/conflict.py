# external
from graphviz.backend import ExecutableNotFound
from html2text import html2text
from jinja2 import Environment, PackageLoader


env = Environment(
    loader=PackageLoader('dephell', 'templates'),
)


def analize_conflict(resolver, suffix: str = '') -> str:
    try:
        resolver.graph.draw(suffix=suffix)
    except ExecutableNotFound:
        print('GraphViz is not installed yet.')

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
