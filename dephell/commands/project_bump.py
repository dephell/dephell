# built-in
from argparse import ArgumentParser
from pathlib import Path
from typing import Iterator

# external
from dephell_discover import Root as PackageRoot
from dephell_versioning import bump_version, bump_file

# app
from ..actions import git_commit, git_tag
from ..config import builders
from ..converters import CONVERTERS
from ..models import Requirement
from .base import BaseCommand


FILE_NAMES = (
    '__init__.py',
    '__version__.py',
    '__about__.py',
    '_version.py',
    '_about.py',
)


class ProjectBumpCommand(BaseCommand):
    """Bump project version.

    https://dephell.readthedocs.io/cmd-project-bump.html
    """
    @classmethod
    def get_parser(cls) -> ArgumentParser:
        parser = ArgumentParser(
            prog='dephell project bump',
            description=cls.__doc__,
        )
        builders.build_config(parser)
        builders.build_from(parser)
        builders.build_output(parser)
        builders.build_api(parser)
        builders.build_other(parser)
        parser.add_argument('--tag', help='create git tag')
        parser.add_argument('name', help='bumping rule name or new version')
        return parser

    def __call__(self) -> bool:
        old_version = None
        root = None
        loader = None
        package = PackageRoot(path=Path(self.config['project']))

        if 'from' in self.config:
            # get project metainfo
            loader = CONVERTERS[self.config['from']['format']]
            root = loader.load(path=self.config['from']['path'])
            if root.version != '0.0.0':
                package = root.package
                old_version = root.version
            else:
                self.logger.warning('cannot get version from `from` file')
        else:
            self.logger.warning('`from` file is not specified')

        if old_version is None and package.metainfo:
            old_version = package.metainfo.version

        if old_version is None:
            if self.args.name == 'init':
                old_version = ''
            else:
                self.logger.error('cannot find old project version')
                return False

        # make new version
        new_version = bump_version(
            version=old_version,
            rule=self.args.name,
            scheme=self.config['versioning'],
        )
        self.logger.info('generated new version', extra=dict(
            old=old_version,
            new=new_version,
        ))

        # update version in project files
        paths = []
        for path in self._bump_project(project=package, old=old_version, new=new_version):
            paths.append(path)
            self.logger.info('file bumped', extra=dict(path=str(path)))

        # update version in project metadata
        updated = self._update_metadata(root=root, loader=loader, new_version=new_version)
        if updated:
            paths.append(Path(self.config['from']['path']))

        # set git tag
        tagged = True
        if self.config.get('tag') is not None:
            tagged = self._add_git_tag(paths=paths, new_version=new_version, template=self.config['tag'])

        return tagged

    @staticmethod
    def _bump_project(project: PackageRoot, old: str, new: str) -> Iterator[Path]:
        for package in project.packages:
            for path in package:
                if path.name not in FILE_NAMES:
                    continue
                file_bumped = bump_file(path=path, old=old, new=new)
                if file_bumped:
                    yield path

    def _update_metadata(self, root, loader, new_version) -> bool:
        if root is None:
            return False
        if root.version == '0.0.0':
            return False

        # we can reproduce metadata only for poetry yet
        if self.config['from']['format'] == 'poetry':
            root.version = new_version
            loader.dump(
                project=root,
                path=self.config['from']['path'],
                reqs=[Requirement(dep=dep, lock=loader.lock) for dep in root.dependencies],
            )
            return True

        # try to replace version in file as string
        path = Path(self.config['from']['path'])
        with path.open('r', encoding='utf8') as stream:
            content = stream.read()
        new_content = content.replace(str(root.version), str(new_version))
        if new_content == content:
            self.logger.warning('cannot bump version in metadata file')
            return False
        with path.open('w', encoding='utf8') as stream:
            stream.write(new_content)
        return True

    def _add_git_tag(self, paths, new_version, template: str) -> bool:
        if '{version}' not in template:
            # add placeholder to the end if it isn't specified
            template += '{version}'
        tag_name = template.format(version=new_version)
        project = Path(self.config['project'])
        if not (project / '.git').exists():
            self.logger.error("project doesn't contain .git in the root folder, cannot create git tag")
            return False

        self.logger.info('commit and tag')
        ok = git_commit(
            message='bump version to {}'.format(str(new_version)),
            paths=paths,
            project=project,
        )
        if not ok:
            self.logger.error('cannot commit files')
            return False
        ok = git_tag(
            name=tag_name,
            project=project,
        )
        if not ok:
            self.logger.error('cannot add tag into git repo')
            return False

        self.logger.info('tag created, do not forget to push it: git push --tags')

        return True
