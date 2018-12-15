# external
import tomlkit

# app
from ..models import Constraint, Dependency, RootDependency
from .base import BaseConverter
from ..links import DirLink


class PoetryLockConverter(BaseConverter):
    lock = True
    fields = (
        'category', 'description', 'name', 'marker', 'optional',
        'python-versions', 'version', 'dependencies',
    )
    # fields for dependency: python, version, platform

    def loads(self, content) -> RootDependency:
        doc = tomlkit.parse(content)

        deps = []
        root = RootDependency()
        if 'package' in doc:
            for content in doc['package']:
                deps.append(self._make_dep(root=root, content=content))
        root.attach_dependencies(deps)
        return root

    def dumps(self, reqs, project: RootDependency, content=None) -> str:
        if content:
            doc = tomlkit.parse(content)
        else:
            doc = tomlkit.document()

        doc['package'] = tomlkit.aot()
        for req in reqs:
            doc['package'].append(self._format_req(req=req))

        doc['metadata'] = {
            'content-hash': ...,
            'platform': '*',
            'python-versions': '*',
        }

        doc['metadata']['hashes'] = tomlkit.table()
        for req in reqs:
            if req.hashes:
                doc['metadata']['hashes'][req.name] = list(req.hashes)

        return tomlkit.dumps(doc)

    # https://github.com/sdispater/tomlkit/blob/master/pyproject.toml
    @staticmethod
    def _make_dep(root, content) -> Dependency:
        # get link
        if 'source' in content:
            url = content['source']['url']
            if content['source']['type'] == 'git':
                url = 'git+' + url
                if 'reference' in content['source']:
                    url += '@' + content['source']['reference']

        return Dependency.from_params(
            raw_name=content['name'],
            description=content['description'],
            constraint=Constraint(root, content['version']),
            marker=content.get('marker', None),
            url=url,
            editable=False,
        )

    def _format_req(self, req):
        result = tomlkit.table()
        for name, value in req:
            if name in self.fields:
                if isinstance(value, tuple):
                    value = list(value)
                result[name] = value
        if 'version' not in result:
            result['version'] = '*'

        # add link
        if req.link:
            result['source'] = tomlkit.table()
            if req.link.git:
                result['source']['type'] = 'git'
            elif isinstance(req.link, DirLink):
                result['source']['type'] = 'directory'
            else:
                result['source']['type'] = 'legacy'
            result['source']['url'] = req.link.short
            if req.rev:
                result['source']['reference'] = req.rev

        # add dependencies
        deps = req.dep.dependencies
        if deps:
            result['dependencies'] = tomlkit.table()
            for dep in deps:
                result['dependencies'][dep.name] = str(dep.constraint)

        return result
