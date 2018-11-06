from ..console import output
from ..controllers import analize_conflict
from ..converters import CONVERTERS
from ..models import Requirement

from .base import BaseCommand


class ConvertCommand(BaseCommand):
    def __call__(self):
        loader = CONVERTERS[self.config['from']['format']]
        dumper = CONVERTERS[self.config['to']['format']]

        # load
        resolver = loader.load_resolver(path=self.config['from']['path'])

        # resolve
        if not loader.lock and dumper.lock:
            resolved = resolver.resolve(progress=True)
            if not resolved:
                conflict = analize_conflict(resolver=resolver)
                output.writeln('<error>Conflict has found:</error> ')
                output.writeln(conflict)
                return False

        # dump
        output.writeln('<info>Resolved!</info>')
        dumper.dump(
            path=self.config['to']['path'],
            reqs=Requirement.from_graph(resolver.graph, lock=dumper.lock),
        )
        return True
