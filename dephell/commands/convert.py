from ..controllers import analize_conflict
from ..console import Progress, output
from ..converters import CONVERTERS
from cleo import Command


class ConvertCommand(Command):
    """
    Convert dependencies between formats.

    convert
        {from-format : format of input file}
        {from-path : path to input file}
        {to-format : format of output file}
        {to-path : path to output file}
    """

    def handle(self):
        loader = CONVERTERS[self.argument('from-format')]
        dumper = CONVERTERS[self.argument('to-format')]

        # load
        resolver = loader.load_resolver(path=self.argument('from-path'))

        # resolve
        if not loader.lock and dumper.lock:
            with Progress().auto():
                resolved = resolver.resolve()
            if not resolved:
                conflict = analize_conflict(graph=resolver.graph)
                output.writeln('<error>CONFLICT:</error> ' + conflict)
                return 1

        # dump
        output.writeln('<info>Resolved!</info>')
        dumper.dump(
            path=self.argument('to-path'),
            graph=resolver.graph,
        )
