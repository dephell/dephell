from jinja2 import Environment, PackageLoader


env = Environment(
    loader=PackageLoader('yourapplication', 'templates'),
)


def analize_conflict(graph):
    conflict = graph.conflict.name
    constraint = str(graph.conflict.constraint)
    return '{} {}'.format(conflict, constraint)
