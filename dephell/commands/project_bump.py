# built-in
from argparse import ArgumentParser
from pathlib import Path

# external
from dephell_discover import Root as PackageRoot

# app
from ..actions import bump_project, bump_version, get_version_from_project, git_commit, git_tag
from ..config import builders
from ..converters import CONVERTERS
from ..models import Requirement
from .base import BaseCommand


class ProjectBumpCommand(BaseCommand):
    """Bump project version.

    https://dephell.readthedocs.io/en/latest/cmd-project-bump.html
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
        parser.add_argument('name', help='bumping rule name or new version')
        return parser

    def __call__(self) -> bool:
        old_version = None
        root = None
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

        if old_version is None:
            old_version = get_version_from_project(project=package)

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
        for path in bump_project(project=package, old=old_version, new=new_version):
            paths.append(path)
            self.logger.info('file bumped', extra=dict(path=str(path)))

        # update version in project metadata
        if root is not None and root.version != '0.0.0':
            # we can reproduce metadata only for poetry yet
            if self.config['from']['format'] == 'poetry':
                paths.append(Path(self.config['from']['path']))
                root.version = new_version
                loader.dump(
                    project=root,
                    path=self.config['from']['path'],
                    reqs=[Requirement(dep=dep, lock=loader.lock) for dep in root.dependencies],
                )
            else:
                path = Path(self.config['from']['path'])
                with path.open('r', encoding='utf8') as stream:
                    content = stream.read()
                new_content = content.replace(str(root.version), str(new_version))
                if new_content == content:
                    self.logger.warning('cannot bump version in metadata file')
                else:
                    with path.open('w', encoding='utf8') as stream:
                        stream.write(new_content)

        # set git tag
        project = Path(self.config['project'])
        if (project / '.git').exists():
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
                name='v.' + str(new_version),
                project=project,
            )
            if not ok:
                self.logger.error('cannot add tag into git repo')
                return False

            self.logger.info('tag created, do not forget to push it: git push --tags')

        return True
