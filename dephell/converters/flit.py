from pathlib import Path

# external
from dephell_specifier import RangeSpecifier
from packaging.requirements import Requirement
from tomlkit import document, dumps, parse

# app
from ..controllers import DependencyMaker, Readme
from .base import BaseConverter
from ..models import RootDependency, Author, EntryPoint
from .egginfo import EggInfoConverter


class FlitConverter(BaseConverter):
    lock = False

    def loads(self, content: str) -> RootDependency:
        doc = parse(content)
        section = doc['tool']['flit']['metadata']
        root = RootDependency(
            raw_name=section.get('dist-name') or section['module'],
            python=RangeSpecifier(section.get('requires-python')),
            classifiers=section.get('classifiers', tuple()),
            license=section.get('license', ''),
            keywords=tuple(section.get('keywords', '').split(',')),
        )

        # description
        if 'description-file' in section:
            root.readme = Readme(path=section['description-file'])

        # entrypoints
        entrypoints = []
        path = Path(section.get('entry-points-file', 'entry_points.txt'))
        if path.exists():
            with path.open('rb', encoding='utf-8') as stream:
                tmp_root = EggInfoConverter().parse_entrypoints(content=stream.read())
                entrypoints = list(tmp_root.entrypoints)
        for group, subentrypoints in section.get('entrypoints', {}).items():
            for entrypoint in subentrypoints:
                entrypoints.append(EntryPoint.parse(text=entrypoint, group=group))
        for entrypoint in section.get('scripts', {}).values():
            entrypoints.append(EntryPoint.parse(text=entrypoint))
        root.entrypoints = tuple(entrypoints)

        # authors
        authors = []
        if 'author' in section:
            authors.append(Author(
                name=section['author'],
                mail=section['author-email'],
            ))
        if 'maintainer' in section:
            authors.append(Author(
                name=section['maintainer'],
                mail=section['maintainer-email'],
            ))
        root.authors = tuple(authors)

        # links
        if 'home-page' in section:
            root.links['home'] = section['home-page']
        if 'urls' in section:
            root.links.update(section['urls'])

        # requirements
        for req in section['requires']:
            root.attach_dependencies(DependencyMaker.from_requirement(
                source=root,
                req=Requirement(req),
            ))
        for req in section['dev-requires']:
            root.attach_dependencies(DependencyMaker.from_requirement(
                source=root,
                req=Requirement(req),
                envs={'dev'},
            ))

        # extras
        for extra, reqs in section.get('requires-extra', {}).items():
            for req in reqs:
                req = Requirement(req)
                root.attach_dependencies(DependencyMaker.from_requirement(
                    source=root,
                    req=req,
                    envs={'main', extra},
                ))

        return root

    def dumps(self, reqs, project: RootDependency, content=None) -> str:
        doc = document()
        ...
        return dumps(doc)

    def _format_req(self, req):
        line = req.name
        if req.extras:
            line += '[{extras}]'.format(extras=','.join(req.extras))
        line += req.version
        if req.markers:
            line += '; ' + req.markers
        return line
