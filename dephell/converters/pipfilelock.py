# built-in
import json
from collections import OrderedDict
from hashlib import sha256
from pathlib import Path
from typing import Optional

# external
from dephell_pythons import Pythons
from dephell_specifier import RangeSpecifier

# app
from ..models import RootDependency
from .pipfile import PIPFileConverter


# https://stackoverflow.com/a/23820416
# https://github.com/pypa/pipfile/blob/master/examples/Pipfile.lock
# https://github.com/pypa/pipfile/blob/master/pipfile/api.py


class PIPFileLockConverter(PIPFileConverter):
    lock = True

    def can_parse(self, path: Path, content: Optional[str] = None) -> bool:
        if isinstance(path, str):
            path = Path(path)
        if content:
            return ('pipfile-spec' in content and 'sha256' in content)
        else:
            return (path.name == 'Pipfile.lock')

    def loads(self, content) -> RootDependency:
        doc = json.loads(content, object_pairs_hook=OrderedDict)
        deps = []
        root = RootDependency(raw_name=self._get_name(content=content))

        python = doc.get('requires', {}).get('python_version', '')
        if python not in {'', '*'}:
            root.python = RangeSpecifier('==' + python)

        for section, is_dev in [('default', False), ('develop', True)]:
            for name, content in doc.get(section, {}).items():
                subdeps = self._make_deps(root, name, content)
                for dep in subdeps:
                    dep.envs = {'dev'} if is_dev else {'main'}
                deps.extend(subdeps)
        root.attach_dependencies(deps)
        return root

    def dumps(self, reqs, project: RootDependency, content=None) -> str:
        packages = {True: OrderedDict(), False: OrderedDict()}
        for req in reqs:
            packages[req.is_dev][req.name] = dict(self._format_req(req=req))

        python = Pythons(abstract=True).get_by_spec(project.python)
        data = OrderedDict([
            ('_meta', OrderedDict([
                ('sources', [OrderedDict([
                    ('url', 'https://pypi.python.org/simple'),
                    ('verify_ssl', True),
                    ('name', 'pypi'),
                ])]),
                ('requires', {'python_version': str(python.version)}),
            ])),
            ('default', packages[False]),
            ('develop', packages[True]),
        ])
        data['_meta']['hash'] = {'sha256': self._get_hash(data)}
        data['_meta']['pipfile-spec'] = 6
        return json.dumps(data, indent=4, separators=(',', ': '))

    @staticmethod
    def _get_hash(data: dict) -> str:
        content = json.dumps(data, sort_keys=True, separators=(',', ':'))
        return sha256(content.encode('utf8')).hexdigest()

    def _format_req(self, req):
        result = dict()
        for name, value in req:
            if name == 'rev':
                name = 'ref'
            if name in self.fields:
                result[name] = value
        return result
