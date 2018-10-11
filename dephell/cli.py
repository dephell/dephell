import argparse

from .config import Config
from .console import Progress, output
from .controllers import analize_conflict
from .converters import CONVERTERS


parser = argparse.ArgumentParser(
    description='Lock and convert dependencies between formats.',
)
parser.add_argument('-c', '--config', default='pyproject.toml', help='path to config file')
parser.add_argument('-e', '--env', default='main', help='environment')


def resolve(rule) -> bool:
    loader = CONVERTERS[rule['from']['format']]
    dumper = CONVERTERS[rule['to']['format']]

    # load
    resolver = loader.load_resolver(path=rule['from']['path'])

    # resolve
    if not loader.lock and dumper.lock:
        with Progress().auto():
            resolved = resolver.resolve()
        if not resolved:
            conflict = analize_conflict(graph=resolver.graph)
            output.writeln('<error>CONFLICT:</error> ' + conflict)
            return False

    # dump
    output.writeln('<info>Resolved!</info>')
    dumper.dump(
        path=rule['to']['path'],
        graph=resolver.graph,
    )
    return True


def main(args):
    args = parser.parse_args(args)
    rule = Config.load(args.config).get(args.env)
    result = resolve(rule)
    return int(not result)
