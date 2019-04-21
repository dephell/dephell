# built-in
from argparse import ArgumentParser
from pathlib import Path

# external
import tomlkit

# app
from ..actions import make_travis
from ..config import builders
from .base import BaseCommand


class GenerateTravisCommand(BaseCommand):
    """Create .travis.yml for DepHell-based project.

    https://dephell.readthedocs.io/en/latest/cmd-generate-travis.html

    https://docs.travis-ci.com/user/languages/python/
    https://docs.travis-ci.com/user/customizing-the-build
    """
    @classmethod
    def get_parser(cls) -> ArgumentParser:
        parser = ArgumentParser(
            prog='dephell generate travis',
            description=cls.__doc__,
        )
        builders.build_config(parser)
        builders.build_output(parser)
        builders.build_other(parser)
        return parser

    def __call__(self) -> bool:
        if self.args.config:
            path = Path(self.args.config)
        else:
            path = Path(self.config['project']) / 'pyproject.toml'
            if not path.exists():
                self.logger.error('cannot generate .travis.yml without config')
                return False

        with path.open('r', encoding='utf8') as stream:
            config = tomlkit.parse(stream.read())
        config = dict(config['tool']['dephell'])
        content = make_travis(config=config)
        if content is None:
            self.logger.error('cannot find appreciate envs in config')
            return False

        path = Path(self.config['project']) / '.travis.yml'
        path.write_text(content)
        self.logger.info('Travis CI config (.travis.yml) generated')
        return True
