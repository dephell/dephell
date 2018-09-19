from operator import attrgetter
from tomlkit import parse, aot, table, document, dumps, inline_table
from ..models import Dependency, RootDependency, Constraint
from ..repositories import get_repo
from .base import BaseConverter


class PIPFileConverter(BaseConverter):
    lock = False

    def loads(self, content) -> RootDependency:
        doc = parse(content)
        deps = []
        root = RootDependency()
        if 'packages' in doc:
            for name, content in doc['packages'].items():
                deps.append(self._make_dep(root, name, content))
        root.attach_dependencies(deps)
        return root

    def dumps(self, graph) -> str:
        doc = document()
        source = table()
        source['url'] = 'https://pypi.python.org/simple'
        source['verify_ssl'] = True
        source['name'] = 'pypi'
        sources = aot()
        sources.append(source)
        doc.add('source', sources)

        deps = table()
        for dep in sorted(graph.mapping.values(), key=attrgetter('name')):
            if not dep.used:
                continue
            deps[dep.name] = self._format_dep(dep)
        doc.add('packages', deps)

        return dumps(doc)

    # https://github.com/pypa/pipfile/blob/master/examples/Pipfile
    @staticmethod
    def _make_dep(root, name, content):
        if isinstance(content, str):
            return Dependency(
                raw_name=name,
                constraint=Constraint(root, content),
                repo=get_repo(),
            )

        # https://github.com/sarugaku/requirementslib/blob/master/src/requirementslib/models/utils.py
        version = content['version'] if 'version' in content else ''

        # https://github.com/sarugaku/requirementslib/blob/master/src/requirementslib/models/requirements.py
        # https://github.com/pypa/pipenv/blob/master/pipenv/project.py
        return Dependency(
            raw_name=name,
            constraint=Constraint(root, version),
            repo=get_repo(),
            extras=set(content.get('extras', [])),
            marker=content.get('markers'),
        )

    @staticmethod
    def _format_dep(dep):
        result = inline_table()
        result['version'] = str(dep.constraint) or '*'
        if dep.extras:
            result['extras'] = list(sorted(dep.extras))
        if dep.marker:
            result['markers'] = str(dep.marker)

        # if we have only version, return string instead of table
        if tuple(result.value) == ('version', ):
            return result['version']

        # do not specify version explicit
        if result['version'] == '*':
            del result['version']

        return result
