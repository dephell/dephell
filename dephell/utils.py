# built-in
import os
from contextlib import contextmanager
from itertools import product


@contextmanager
def chdir(path):
    """Context manager for changing dir and restoring previous workdir after exit.
    """
    curdir = os.getcwd()

    path = str(path)
    if not os.path.exists(path):
        os.makedirs(path)

    os.chdir(path)
    try:
        yield
    finally:
        os.chdir(curdir)


def lazy_product(*all_groups):
    slices = [[] for _ in range(len(all_groups))]
    all_groups = [iter(groups) for groups in all_groups]

    while True:
        has_tail = False
        tail = []
        for container, groups in zip(slices, all_groups):
            group = next(groups, None)
            tail.append(group)
            if group is not None:
                container.append(group)
                has_tail = True
        if not has_tail:
            return

        for groups in product(*slices):
            for group, el in zip(groups, tail):
                if el is not None and group == el:
                    yield groups
                    break
