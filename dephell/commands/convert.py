from cached_property import cached_property
from ..config import Config, parser
from ..console import Progress, output
from ..controllers import analize_conflict
from ..converters import CONVERTERS


class ConvertCommand:
    parser = parser

    def __init__(self, args):
        self.args = args

    @cached_property
    def config(self):
        config = Config()
        config.attach_file(path=self.args.config, env=self.args.env)
        config.attach_cli(self.args)
        return config

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
