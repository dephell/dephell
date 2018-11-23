# external
import attr


@attr.s()
class Author:
    name = attr.ib()
    mail = attr.ib()

    def __str__(self):
        return '{name} <{mail}>'.format(name=self.name, mail=self.mail)
