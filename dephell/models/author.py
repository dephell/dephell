# external
import attr


@attr.s()
class Author:
    name = attr.ib()
    mail = attr.ib()

    def __str__(self):
        return '{} <{}>'.format(self.name, self.mail)
