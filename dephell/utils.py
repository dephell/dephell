# built-in
from itertools import product


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


# https://github.com/bottlepy/bottle/commit/fa7733e075da0d790d809aa3d2f53071897e6f76
# https://github.com/pydanny/cached-property/blob/master/cached_property.py
class cached_property(object):  # noqa: N801
    """
    A property that is only computed once per instance and then replaces itself
    with an ordinary attribute. Deleting the attribute resets the property.
    """
    def __init__(self, func):
        self.__doc__ = func.__doc__
        self.func = func

    def __get__(self, obj, cls):
        if obj is None:
            return self
        value = obj.__dict__[self.func.__name__] = self.func(obj)
        return value
