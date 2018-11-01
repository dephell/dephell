from ..console import Progress, output
from ..controllers import analize_conflict
from ..converters import CONVERTERS

from .base import BaseCommand


class ConvertCommand(BaseCommand):
    def __call__(self):
        loader = CONVERTERS[self.config['from']['format']]
        dumper = CONVERTERS[self.config['to']['format']]

        # load
        resolver = loader.load_resolver(path=self.config['from']['path'])

        # resolve
        if not loader.lock and dumper.lock:
            with Progress().auto():
                resolved = resolver.resolve()
            if not resolved:
                conflict = analize_conflict(resolver=resolver)
                output.writeln('<error>CONFLICT:</error> ' + conflict)
                return False

        # dump
        output.writeln('<info>Resolved!</info>')
        dumper.dump(
            path=self.config['to']['path'],
            graph=resolver.graph,
        )
        return True
