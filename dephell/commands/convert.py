import huepy

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
        should_be_resolved = not loader.lock and dumper.lock

        # attach
        if self.config.get('and'):
            for source in self.config['and']:
                loader = CONVERTERS[source['format']]
                root = loader.load(path=source['path'])
                resolver.graph.add(root)

            # merge (without full graph building)
            if not should_be_resolved:
                resolved = resolver.resolve(progress=True, level=1)
                if not resolved:
                    conflict = analize_conflict(resolver=resolver)
                    print(huepy.bad('Conflict has found:'))
                    print(conflict)
                    return False
                print(huepy.good('Merged!'))

        # resolve (and merge)
        if should_be_resolved:
            resolved = resolver.resolve(progress=True)
            if not resolved:
                conflict = analize_conflict(resolver=resolver)
                print(huepy.bad('Conflict has found:'))
                print(conflict)
                return False
            print(huepy.good('Resolved!'))

        # dump
        dumper.dump(
            path=self.config['to']['path'],
            reqs=Requirement.from_graph(resolver.graph, lock=dumper.lock),
        )
        return True
