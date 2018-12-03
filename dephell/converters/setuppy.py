# built-in
from distutils.core import run_setup
from itertools import chain

# external
from packaging.requirements import Requirement

# app
from ..models import Dependency, RootDependency, Author
from .base import BaseConverter


class SetupPyConverter(BaseConverter):
    lock = False

    @classmethod
    def load(cls, path) -> RootDependency:
        info = run_setup(str(path))

        root = RootDependency(
            raw_name=cls._get(info, 'name'),
            version=cls._get(info, 'version') or '0.0.0',

            description=cls._get(info, 'summary'),
            license=cls._get(info, 'license'),
            long_description=cls._get(info, 'description'),

            keywords=cls._get(info, 'keywords').split(','),
            classifiers=cls._get_list(info, 'classifiers'),
            platforms=cls._get_list(info, 'platforms'),
        )

        # links
        for key, name in (('home', 'url'), ('download', 'download_url')):
            link = cls._get(info, name)
            if link:
                root.links[key] = link

        # authors
        for name in ('author', 'maintainer'):
            author = cls._get(info, name)
            if author:
                root.authors += (
                    Author(name=author, mail=cls._get(info, name + '_email')),
                )

        reqs = chain(
            cls._get_list(info, 'requires'),
            cls._get_list(info, 'install_requires'),
        )
        deps = []
        for req in reqs:
            req = Requirement(req)
            deps.append(Dependency.from_requirement(source=root, req=req))
        root.attach_dependencies(deps)
        return root

    def dumps(self, reqs, content=None) -> str:
        raise NotImplementedError('dumping to setup.py is not supported yet')

    # private methods

    @staticmethod
    def _get(msg, name: str) -> str:
        value = getattr(msg.metadata, name, None)
        if not value:
            value = getattr(msg, name, None)
        if not value:
            return ''
        if value == 'UNKNOWN':
            return ''
        return value.strip()

    @staticmethod
    def _get_list(msg, name: str) -> tuple:
        values = getattr(msg, name, None)
        if not values:
            return ()
        return tuple(value for value in values if value != 'UNKNOWN')
