
class Mutator:
    def __init__(self):
        ...

    def mutate(self, mapping):
        """Get conflicting mapping part and mutate one dependency.

        Mutation changes group for one from dependencies
        from parents of conflicting dependency.
        """
        ...

    def check(self, mapping):
        ...

    def remember(self, mapping):
        ...

    def inject(self, mapping, dep):
        ...
