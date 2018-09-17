from ..core import load, dump, analize_conflict
from ..console import Progress, output
from cleo import Command


class ConvertCommand(Command):
    """
    Convert dependencies between formats.

    convert
        {from-format : format of input file}
        {from-path : path to input file}
        {to-format : format of output file}
        {to-path : path to output file}
        {--tl|to-lock : lock requirements}
    """

    def handle(self):
        # load
        resolver = load(
            loader=self.argument('from-format'),
            path=self.argument('from-path'),
        )

        # resolve
        if self.option('to-lock'):
            with Progress().auto():
                resolved = resolver.resolve()
        else:
            resolved = True

        # dump
        if resolved:
            output.writeln('<info>Resolved!</info>')
            dump(
                dumper=self.argument('to-format'),
                path=self.argument('to-path'),
                graph=resolver.graph,
            )
        else:
            conflict = analize_conflict(graph=resolver.graph)
            output.writeln('<error>CONFLICT:</error> ' + conflict)
        return 1 - int(resolved)
