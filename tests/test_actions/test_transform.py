from pathlib import Path

import pytest
from bowler import Query

from dephell.actions import transform_imports


@pytest.mark.parametrize('code_in, code_out, old_name, new_name', [
    # module import
    ('import astana', 'import nursultan as astana', 'astana', 'nursultan'),
    ('import astana', 'import nurs.ultan as astana', 'astana', 'nurs.ultan'),
    ('import foo', 'import foo', 'bar', 'baz'),
    ('import foo, bar', 'import baz as foo, bar', 'foo', 'baz'),
    ('import bar, foo', 'import bar, baz as foo', 'foo', 'baz'),
    # ('import foo.bar', 'from baz.bar', 'foo', 'baz'),

    # from import
    ('from foo import bar', 'from baz import bar', 'foo', 'baz'),
    ('from root.foo import bar', 'from baz import bar', 'root.foo', 'baz'),
    ('from foo import bar', 'from root.baz import bar', 'foo', 'root.baz'),
    ('from foo import bar, baz', 'from baz import bar, baz', 'foo', 'baz'),
    ('from foo import bar, foo', 'from baz import bar, foo', 'foo', 'baz'),
    ('from foo.bar import baz', 'from root.bar import baz', 'foo', 'root'),

    # as import
    ('import foo as bar', 'import baz as bar', 'foo', 'baz'),
    ('import root.foo as bar', 'import baz as bar', 'root.foo', 'baz'),
    ('import foo.sub as bar', 'import baz.sub as bar', 'foo', 'baz'),
    ('import foo as bar, boo', 'import baz as bar, boo', 'foo', 'baz'),
    ('import boo, foo as bar', 'import boo, baz as bar', 'foo', 'baz'),
    ('import boo, root.foo as bar', 'import boo, baz as bar', 'root.foo', 'baz'),
    ('import boo, root.foo as bar', 'import boo, baz.foo as bar', 'root', 'baz'),
    ('import boo as foo', 'import boo as foo', 'foo', 'baz'),

    # string replacement
    ('del sys.modules["foo"]', 'del sys.modules["bar"]', 'foo', 'bar'),
    ('del sys.modules["foo.baz"]', 'del sys.modules["bar.baz"]', 'foo', 'bar'),
    ("del sys.modules['foo.baz']", "del sys.modules['bar.baz']", 'foo', 'bar'),

    # ('import foo.bar\nfoo.bar.test()', 'import baz.bar\nbaz.bar.test()', 'foo', 'baz'),
    # (
    #     'import old.foo.bar\nold.foo.bar.test()',
    #     'import new.baz.bar\nnew.baz.bar.test()',
    #     'old.foo', 'new.baz',
    # ),
])
def test_transform_imports(code_in: str, code_out: str, old_name: str, new_name: str, temp_path: Path):
    code_in += '\n'
    code_out += '\n'
    path = temp_path / 'tmp.py'
    path.write_text(code_in)
    query = transform_imports(query=Query(str(path)), old_name=old_name, new_name=new_name)
    query.execute(silent=True, write=True, interactive=False)
    result = path.read_text()
    if code_in == code_out:
        assert result == code_out, 'unexpected changes'
    else:
        assert result != code_in, 'nothing was changed'
        assert result == code_out, 'invalid changes'
