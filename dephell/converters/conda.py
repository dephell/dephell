from io import StringIO
from pathlib import Path
from typing import Optional

from ..yaml import yaml_dump, yaml_load
from dephell_specifier import RangeSpecifier
from packaging.utils import canonicalize_name

from ..controllers import DependencyMaker
from ..models import RootDependency
from ..repositories import CondaRepo
from .base import BaseConverter


class CondaConverter(BaseConverter):
    def can_parse(self, path: Path, content: Optional[str] = None) -> bool:
        if isinstance(path, str):
            path = Path(path)
        return path.name in ('environment.yml', 'environment.yaml')

    # https://github.com/ericmjl/conda-envs/blob/master/deeplearning.yml
    def loads(self, content: str) -> RootDependency:
        doc = yaml_load(content)
        root = RootDependency(raw_name=doc.get('name') or self._get_name(content=content))
        repo = CondaRepo(channels=doc.get('channels', []))
        for req in doc.get('dependencies', []):
            parsed = repo.parse_req(req)
            if parsed['name'] == 'python':
                if parsed.get('version', '*') not in ('*', ''):
                    spec = '.'.join((parsed['version'].split('.') + ['*', '*'])[:3])
                    root.python = RangeSpecifier(spec)
                continue
            root.attach_dependencies(DependencyMaker.from_params(
                raw_name=parsed['name'],
                constraint=parsed.get('version', '*'),
                source=root,
                repo=repo,
            ))
        return root

    def dumps(self, reqs, project: Optional[RootDependency] = None,
              content: Optional[str] = None) -> str:
        if content:
            doc = yaml_load(content, safe=False)
        else:
            doc = dict()

        doc['name'] = project.name

        # channels

        if 'channels' not in doc:
            doc['channels'] = []
        channels = set()
        # get channels
        for req in reqs:
            if isinstance(req.dep.repo, CondaRepo):
                channels.update(req.dep.repo.channels)
        # remove old channels
        for index, channel in reversed(list(enumerate(doc['channels']))):
            if channel not in channels:
                del doc['channels'][index]
        # add new channels
        for channel in channels:
            if channel not in doc['channels']:
                doc['channels'].append(channel)
        # add default channel
        if not doc['channels']:
            doc['channels'] = ['defaults']

        # dependencies

        if 'dependencies' not in doc:
            doc['dependencies'] = []
        deps = {req.name: req.version for req in reqs}
        # remove old deps
        represented = set()
        for index, dep in reversed(list(enumerate(doc['dependencies']))):
            parsed = CondaRepo.parse_req(dep)
            name = canonicalize_name(parsed['name'])
            represented.add(name)
            if name not in deps:
                # remove
                del doc['dependencies'][index]
            elif parsed.get('version', '*') != deps[name]:
                # update
                dep = name if deps[name] in ('', '*') else '{} {}'.format(name, deps[name])
                doc['dependencies'][index] = dep
        # add new deps
        for name, version in sorted(deps.items()):
            if name in represented:
                continue
            dep = name if version in ('', '*') else '{} {}'.format(name, version)
            doc['dependencies'].append(dep)
        # drop empty section
        if not doc['dependencies']:
            del doc['dependencies']

        stream = StringIO()
        yaml_dump(doc, stream)
        stream.seek(0)
        return stream.read()
