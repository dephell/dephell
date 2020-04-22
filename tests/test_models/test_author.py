# external
import pytest

# project
from dephell.models.author import Author


@pytest.mark.parametrize('name, mail, formatted', [
    ('gram',            'example@mail.com',         'gram <example@mail.com>'),
    ('gram',            None,                       'gram'),

    ('Грам @orsinium',  'example_mail@mail.com',    'Грам @orsinium <example_mail@mail.com>'),
    ('Грам @orsinium',  None,                       'Грам @orsinium'),
])
def test_format(name, mail, formatted):
    author = Author(name=name, mail=mail)
    assert str(author) == formatted


@pytest.mark.parametrize('name, mail, formatted', [
    ('gram',            'example@mail.com',         'gram <example@mail.com>'),
    ('gram',            None,                       'gram'),

    ('Грам @orsinium',  'example_mail@mail.com',    'Грам @orsinium <example_mail@mail.com>'),
    ('Грам @orsinium',  None,                       'Грам @orsinium'),
])
def test_parse(name, mail, formatted):
    author = Author.parse(formatted)
    assert author.name == name
    assert author.mail == mail
