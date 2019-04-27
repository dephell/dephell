from io import StringIO
from pathlib import Path
from typing import Optional

from ruamel.yaml import YAML
from dephell_specifier import RangeSpecifier

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
        doc = YAML(typ='safe').load(content)
        root = RootDependency(raw_name=doc.get('name') or self._get_name(content=content))
        repo = CondaRepo(channels=doc.get('channels', []))
        for req in doc.get('dependencies', []):
            name, _sep, spec = req.partition('=')
            spec = '==' + spec if spec else '*'
            if name == 'python':
                spec = '.'.join((spec.split('.') + ['*', '*'])[:3])
                root.python = RangeSpecifier(spec)
                continue
            root.attach_dependencies(DependencyMaker.from_params(
                raw_name=name,
                constraint=spec,
                source=root,
                repo=repo,
            ))
        return root

    def dumps(self, reqs, project: Optional[RootDependency] = None,
              content: Optional[str] = None) -> str:
        yaml = YAML(typ='safe')
        if content:
            doc = yaml.load(content)
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
        deps = {req.name: req.version.strip('<>=') for req in reqs}
        # remove old deps
        for index, dep in reversed(list(enumerate(doc['dependencies']))):
            name, _sep, version = dep.partition('=')
            if name not in deps:
                del doc['dependencies'][index]
        # add new deps
        for name, version in sorted(deps.items()):
            dep = '{}={}'.format(name, version).rstrip('=*')
            if dep not in doc['dependencies']:
                doc['dependencies'].append(dep)
        # drop empty section
        if not doc['dependencies']:
            del doc['dependencies']

        stream = StringIO()
        yaml.dump(doc, stream)
        stream.seek(0)
        return stream.read()
