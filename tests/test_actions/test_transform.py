from pathlib import Path

import pytest
from bowler import Query

from dephell.actions._transform import transform_imports


@pytest.mark.parametrize('code_in, code_out, old_name, new_name', [
    ('import astana', 'import nursultan as astana', 'astana', 'nursultan'),
    ('import astana', 'import nurs.ultan as astana', 'astana', 'nurs.ultan'),
    # ('import ast.ana', 'import nurs.ultan as as.tana', 'ast.ana', 'nurs.ultan'),
    ('import foo', 'import foo', 'bar', 'baz'),
    # ('import foo, bar', 'import foo as baz, bar\n', 'foo', 'baz'),
    # ('from foo import bar', 'from baz import bar', 'foo', 'baz'),
])
def test_transform_as_import(code_in: str, code_out: str, old_name: str, new_name: str, temp_path: Path):
    code_in += '\n'
    code_out += '\n'
    path = temp_path / 'tmp.py'
    path.write_text(code_in)
    q = transform_imports(query=Query(str(path)), old_name=old_name, new_name=new_name)
    q.execute(silent=True, write=True, interactive=False)
    result = path.read_text()
    if code_in == code_out:
        assert result == code_out, 'unexpected changes'
    else:
        assert result != code_in, 'nothing was changed'
        assert result == code_out, 'invalid changes'
