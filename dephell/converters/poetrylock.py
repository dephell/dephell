# built-in
from collections import defaultdict
from pathlib import Path
from typing import List, Optional

# external
import tomlkit
from dephell_links import DirLink
from dephell_specifier import RangeSpecifier

# app
from ..controllers import DependencyMaker, RepositoriesRegistry
from ..models import Constraint, Dependency, RootDependency
from ..repositories import WarehouseBaseRepo, WarehouseLocalRepo
from .base import BaseConverter


class PoetryLockConverter(BaseConverter):
    lock = True
    fields = (
        'category', 'description', 'name', 'marker', 'optional',
        'python-versions', 'version', 'dependencies',
    )
    # fields for dependency: python, version, platform

    def can_parse(self, path: Path, content: Optional[str] = None) -> bool:
        if isinstance(path, str):
            path = Path(path)
        if content:
            return ('[[package]]' in content and '[metadata.hashes]' in content)
        else:
            return (path.name in ('pyproject.lock', 'poetry.lock'))

    def loads(self, content) -> RootDependency:
        doc = tomlkit.parse(content)
        root = RootDependency()
        root.python = RangeSpecifier(doc.get('metadata', {}).get('python-versions', '*'))

        # get repositories
        repo = RepositoriesRegistry()
        if doc.get('source'):
            for source in doc['source']:
                repo.add_repo(url=source['url'], name=source['name'])
        repo.attach_config()

        envs = defaultdict(set)
        for extra, deps in doc.get('extras', {}).items():
            for dep in deps:
                envs[dep].add(extra)
        for content in doc.get('package', []):
            # category can be "dev" or "main"
            envs[content['name']].add(content['category'])

        deps = []
        for content in doc.get('package', []):
            deps.extend(self._make_deps(
                root=root,
                content=content,
                envs=envs[content['name']],
                repo=repo,
            ))
        root.attach_dependencies(deps)
        return root

    def dumps(self, reqs, project: RootDependency, content=None) -> str:
        doc = tomlkit.parse(content) if content else tomlkit.document()
        doc['package'] = [self._format_req(req=req) for req in reqs]

        # add extras
        extras = defaultdict(list)
        for req in reqs:
            if req.is_main:
                for extra in req.main_envs:
                    extras[extra].append(req.name)
            if req.is_dev:
                for extra in req.dev_envs:
                    extras[extra].append(req.name)
        if extras:
            doc['extras'] = dict(extras)

        # add repositories
        sources = tomlkit.aot()
        added = set()
        for req in reqs:
            if not isinstance(req.dep.repo, RepositoriesRegistry):
                continue
            for repo in req.dep.repo.repos:
                if repo.from_config:
                    continue
                if repo.name in added:
                    continue
                if isinstance(repo, WarehouseLocalRepo):
                    continue
                added.add(repo.name)

                source = tomlkit.table()
                source['name'] = repo.name
                source['url'] = repo.pretty_url
                sources.append(source)
        if sources:
            doc['source'] = sources

        doc['metadata'] = {
            # sha256 of tool.poetry section from pyproject.toml
            # 'content-hash': ...,
            # 'platform': '*',
            'python-versions': str(project.python),
        }

        doc['metadata']['hashes'] = tomlkit.table()
        for req in reqs:
            doc['metadata']['hashes'][req.name] = list(req.hashes or [])

        return tomlkit.dumps(doc)

    # https://github.com/sdispater/poetry/blob/master/poetry.lock
    @classmethod
    def _make_deps(cls, root, content, envs, repo) -> List[Dependency]:
        # get link
        url = None
        if 'source' in content:
            if content['source']['type'] == 'legacy':
                repo = repo.make(content['source']['reference'])
            else:
                repo = None
                url = content['source']['url']
                if content['source']['type'] == 'git':
                    url = 'git+' + url
                    if 'reference' in content['source']:
                        url += '@' + content['source']['reference']

        # make markers
        marker = content.get('marker', None)
        if content.get('python-versions', '*') != '*':
            python = RangeSpecifier(content['python-versions']).to_marker('python_version')
            if marker is None:
                marker = python
            else:
                marker = '({}) and {}'.format(marker, python)

        # make version
        version = content['version']
        if version != '*':
            version = '==' + version

        deps = DependencyMaker.from_params(
            raw_name=content['name'],
            description=content.get('description', ''),
            constraint=Constraint(root, version),
            marker=marker,
            url=url,
            editable=False,
            envs=envs,
        )

        if repo is not None:
            for dep in deps:
                dep.repo = repo

        if version == '*':
            return deps

        # add dependencies for dependencies
        subdeps = []
        for subname, subcontent in content.get('dependencies', dict()).items():
            if isinstance(subcontent, list):
                subcontent = ','.join(set(subcontent))
            if isinstance(subcontent, str):
                subdeps.extend(DependencyMaker.from_params(
                    raw_name=subname,
                    constraint=Constraint(root, '==' + subcontent),
                    envs=envs,
                ))
                continue

            if 'python' in subcontent:
                marker = RangeSpecifier(subcontent['python']).to_marker('python_version')
            else:
                marker = None

            if isinstance(subcontent['version'], list):
                subcontent['version'] = ','.join(set(subcontent['version']))
            subdeps.extend(DependencyMaker.from_params(
                raw_name=subname,
                constraint=Constraint(root, subcontent['version']),
                marker=marker,
                envs=envs,
            ))
        deps[0].dependencies = tuple(subdeps)

        return deps

    def _format_req(self, req):
        result = tomlkit.table()
        for name, value in req:
            if name in self.fields:
                if isinstance(value, tuple):
                    value = list(value)
                result[name] = value
        result['category'] = 'dev' if req.is_dev else 'main'
        if 'version' not in result:
            result['version'] = '*'
        result['version'] = result['version'].lstrip('=')
        if req.markers:
            result['marker'] = req.markers

        # add link
        if req.link and (req.git or isinstance(req.link, DirLink)):
            result['source'] = tomlkit.table()
            if req.git:
                result['source']['type'] = 'git'
            elif isinstance(req.link, DirLink):
                result['source']['type'] = 'directory'
            result['source']['url'] = req.link.short
            if req.rev:
                result['source']['reference'] = req.rev
        elif isinstance(req.dep.repo, WarehouseBaseRepo):
            repo = req.dep.repo.repos[0]
            result['source'] = tomlkit.table()
            result['source']['type'] = 'legacy'
            result['source']['url'] = repo.pretty_url
            result['source']['reference'] = repo.name

        # add dependencies
        deps = req.dep.dependencies
        if deps:
            result['dependencies'] = tomlkit.table()
            for dep in deps:
                result['dependencies'][dep.raw_name] = str(dep.constraint) or '*'

        return result
