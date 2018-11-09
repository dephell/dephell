# external
from graphviz.backend import ExecutableNotFound
from html2text import html2text
from jinja2 import Environment, PackageLoader


env = Environment(
    loader=PackageLoader('dephell', 'templates'),
)


def analize_conflict(resolver, suffix: str='') -> str:
    try:
        resolver.graph.draw(suffix=suffix)
    except ExecutableNotFound:
        print('GraphViz is not installed yet.')

    template = env.get_template('state.html.j2')
    content = template.render(
        conflict=resolver.graph.conflict,
        graph=resolver.graph,
        mutator=resolver.mutator,
    )
    return html2text(content)
