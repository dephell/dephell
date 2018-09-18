from tomlkit import parse, array, table, document, dumps, inline_table
from ..models import Dependency, RootDependency, Constraint
from ..repositories import get_repo


class PIPFileConverter:
    lock = False

    def loads(self, path) -> RootDependency:
        with open(str(path), 'r') as stream:
            doc = parse(stream.read())
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
        doc.add('source', array([source]))

        deps = table()
        for dep in graph.mapping.values():
            if not dep.used:
                continue
            deps[dep.name] = self._format_dep(dep)
        deps.sort()

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
        result['version'] = str(dep.constraint)
        if dep.extras:
            result['extras'] = list(sorted(dep.extras))
        if dep.marker:
            result['markers'] = str(dep.marker)
        return result
