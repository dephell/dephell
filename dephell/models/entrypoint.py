from typing import Optional
import attr


@attr.s()
class EntryPoint:
    name = attr.ib(type=str)
    path = attr.ib(type=str)

    extras = attr.ib(type=tuple, default=tuple())
    group = attr.ib(type=str, default='console_scripts')

    @classmethod
    def parse(cls, text: str, group: Optional[str] = None) -> 'EntryPoint':
        name, path = text.split('=', maxsplit=1)
        name = name.strip()
        path = path.strip()
        if '[' not in path:
            return cls(name=name, path=path, group=group)
        path, extras = path.rstrip(']').split('[', maxsplit=1)
        return cls(name=name, path=path, group=group, extras=extras.split(','))

    def __str__(self) -> str:
        result = '{} = {}'.format(self.name, self.path)
        if self.extras:
            result += '[{}]'.format(', '.join(self.extras))
        return result
