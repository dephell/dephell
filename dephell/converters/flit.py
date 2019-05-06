# external
from packaging.requirements import Requirement
from tomlkit import document, dumps, parse

# app
from ..controllers import DependencyMaker
from .base import BaseConverter
from ..models import RootDependency, Author


class FlitConverter(BaseConverter):
    lock = False

    def loads(self, content: str) -> RootDependency:
        doc = parse(content)
        section = doc['tool']['flit']['metadata']
        root = RootDependency(
            raw_name=section['module'],
            classifiers=section.get('classifiers', tuple()),
        )

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

        for req in section['requires']:
            req = Requirement(req)
            root.attach_dependencies(DependencyMaker.from_requirement(source=root, req=req))

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
