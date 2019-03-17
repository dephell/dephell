import attr


@attr.s()
class EntryPoint:
    name = attr.ib(type=str)
    path = attr.ib(type=str)

    extras = attr.ib(type=tuple, default=tuple())
    group = attr.ib(type=str, default='console_scripts')

    def __str__(self) -> str:
        result = '{} = {}'.format(self.name, self.path)
        if self.extras:
            result += '[{}]'.format(', '.join(self.extras))
        return result
