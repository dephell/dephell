# built-in
from pathlib import Path

# external
from editorconfig.fnmatch import fnmatch


HEADER = """
# EditorConfig helps developers define and maintain consistent
# coding styles between different editors and IDEs
# https://editorconfig.org
root = true

[*]
end_of_line = lf
charset = utf-8
trim_trailing_whitespace = true
insert_final_newline = true

"""

RULES = (
    ('*.py', ('indent_style = space', 'indent_size = 4')),
    ('*.{md,rst,txt}', ('indent_style = space', 'indent_size = 4')),
    ('*.{ini,toml}', ('indent_style = space', 'indent_size = 4')),

    ('*.js', ('indent_style = space', 'indent_size = 2')),
    ('*.{json,yml,yaml}', ('indent_style = space', 'indent_size = 2')),
    ('*.{html,j2}', ('indent_style = space', 'indent_size = 2')),

    ('Makefile', ('indent_style = tab', )),
    ('*.go', ('indent_style = tab', )),
)


def make_editorconfig(path: Path) -> str:
    matched = []
    non_matched = list(RULES)
    for path in path.iterdir():
        for i, (match, _rule) in enumerate(non_matched):
            if fnmatch(path.name, match):
                matched.append(non_matched.pop(i))
                break

    matched = ['[{}]\n{}'.format(match, '\n'.join(rule)) for match, rule in matched]
    return HEADER + '\n\n'.join(matched) + '\n'
