import sys
from .core import load, dump, analize_conflict
from .console import Progress, output


USAGE = """
Usage:
{name} from [format] [path] to [format] [path]

Example:
{name} from pip requirements.in to pip requirements.txt
"""


def resolve(args=sys.argv):
    if len(args) < 7 or args[1] != 'from' or args[4] != 'to':
        print(USAGE.format(name='python3 -m dephell'))
        exit()

    resolver = load(loader=args[2], path=args[3])
    with Progress().auto():
        resolved = resolver.resolve()
    if resolved:
        output.writeln('<info>Resolved!</info>')
        dump(dumper=args[5], path=args[6], graph=resolver.graph)
    else:
        conflict = analize_conflict(graph=resolver.graph)
        output.writeln('<error>CONFLICT:</error> ' + conflict)
    return 1 - int(resolved)
