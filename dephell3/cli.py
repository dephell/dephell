import sys
from .core import load, dump, analize_conflict


USAGE = """
Usage:
{args[0]} from [format] [path] to [format] [path]

Example:
{args[0]} from pip requirements.in to pip requirements.txt
"""


def resolve(args=sys.argv):
    if len(args) < 7 or args[1] != 'from' or args[4] != 'to':
        print(USAGE.format(args=args))
        exit()

    resolver = load(loader=args[2], path=args[3])
    resolved = resolver.resolve()
    if resolved:
        dump(dumper=args[5], path=args[6], graph=resolver.graph)
    else:
        print(analize_conflict(graph=resolver.graph), file=sys.stderr)
    return 1 - int(resolved)
