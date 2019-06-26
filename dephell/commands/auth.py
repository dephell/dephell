# built-in
from argparse import ArgumentParser

import tomlkit

# app
from ..config import builders, get_data_dir
from ..constants import GLOBAL_CONFIG_NAME
from .base import BaseCommand


class AuthCommand(BaseCommand):
    """Insert, update or delete credentials.

    https://dephell.readthedocs.io/cmd-auth.html
    """
    _global_config_path = get_data_dir() / GLOBAL_CONFIG_NAME

    @classmethod
    def get_parser(cls) -> ArgumentParser:
        parser = ArgumentParser(
            prog='dephell auth',
            description=cls.__doc__,
        )
        builders.build_config(parser)
        builders.build_output(parser)
        parser.add_argument('hostname', help='server hostname')
        parser.add_argument('username', nargs='?')
        parser.add_argument('password', nargs='?')
        return parser

    def __call__(self) -> bool:
        path = self._global_config_path
        if path.exists():
            doc = tomlkit.parse(path.read_text(encoding='utf8'))
        else:
            doc = tomlkit.document()
        creds = doc.get('auth') or tomlkit.aot()

        hst = self.args.hostname
        usr = self.args.username
        pwd = self.args.password

        # delete all credentials for hostname
        if not usr:
            new = [cred for cred in creds if cred['hostname'] != hst]
            diff = len(creds) - len(new)
            if diff == 0:
                self.logger.error('cannot find credentials to remove', extra=dict(
                    hostname=hst,
                ))
                return False
            doc['auth'] = new
            path.write_text(tomlkit.dumps(doc), encoding='utf8')
            self.logger.info('credentials removed', extra=dict(
                hostname=hst,
                count=diff,
            ))
            return True

        # delete one credential
        if not pwd:
            new = [cred for cred in creds if cred['hostname'] != hst or cred['username'] != usr]
            diff = len(creds) - len(new)
            if diff == 0:
                self.logger.error('cannot find credentials to remove', extra=dict(
                    hostname=hst,
                    username=usr,
                ))
                return False
            doc['auth'] = new
            path.write_text(tomlkit.dumps(doc), encoding='utf8')
            self.logger.info('credentials removed', extra=dict(
                hostname=hst,
                username=usr,
            ))
            return True

        # update
        updated = False
        for cred in creds:
            if cred['hostname'] == hst and cred['username'] == usr:
                cred['password'] = pwd
                updated = True
        if updated:
            doc['auth'] = creds
            path.write_text(tomlkit.dumps(doc), encoding='utf8')
            self.logger.info('credentials updated', extra=dict(
                hostname=hst,
                username=usr,
            ))
            return True

        # add
        cred = tomlkit.table()
        cred['hostname'] = hst
        cred['username'] = usr
        cred['password'] = pwd
        creds.append(cred)
        doc['auth'] = creds
        path.write_text(tomlkit.dumps(doc), encoding='utf8')
        self.logger.info('credentials added', extra=dict(
            hostname=hst,
            username=usr,
        ))
        return True
