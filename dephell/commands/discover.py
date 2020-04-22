# built-in
from importlib import import_module


# keep sorted
_NAMES = (
    'deps add',
    'deps audit',
    'deps check',
    'deps convert',
    'deps install',
    'deps licenses',
    'deps outdated',
    'deps sync',
    'deps tree',

    'docker create',
    'docker destroy',
    'docker prepare',
    'docker run',
    'docker shell',
    'docker stop',
    'docker tags',

    'generate authors',
    'generate config',
    'generate contributing',
    'generate editorconfig',
    'generate license',
    'generate travis',

    'inspect auth',
    'inspect config',
    'inspect gadget',
    'inspect project',
    'inspect self',
    'inspect venv',
    'inspect versioning',

    'jail install',
    'jail list',
    'jail remove',
    'jail show',
    'jail try',

    'package bug',
    'package changelog',
    'package downloads',
    'package install',
    'package list',
    'package purge',
    'package releases',
    'package remove',
    'package search',
    'package show',
    'package verify',

    'project build',
    'project bump',
    'project register',
    'project test',
    'project upload',
    'project validate',

    'self auth',
    'self autocomplete',
    'self uncache',
    'self upgrade',

    'vendor download',
    'vendor import',

    'venv create',
    'venv destroy',
    'venv entrypoint',
    'venv run',
    'venv shell',
)


COMMANDS = dict()
package = __name__.rsplit('.', maxsplit=1)[0]
for name in _NAMES:
    module_name = name.replace(' ', '_')
    class_name = name.title().replace(' ', '') + 'Command'
    module = import_module('.' + module_name, package=package)
    COMMANDS[name] = getattr(module, class_name)
