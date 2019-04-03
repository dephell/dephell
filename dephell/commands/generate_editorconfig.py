# built-in
from argparse import ArgumentParser
from pathlib import Path

# external
from editorconfig.fnmatch import fnmatch

# app
from ..config import builders
from .base import BaseCommand


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


class GenerateEditorconfigCommand(BaseCommand):
    """Create EditorConfig for project.

    https://dephell.readthedocs.io/en/latest/cmd-generate-editorconfig.html
    https://editorconfig.org/
    """
    @classmethod
    def get_parser(cls):
        parser = ArgumentParser(
            prog='dephell generate editorconfig',
            description=cls.__doc__,
        )
        builders.build_config(parser)
        builders.build_output(parser)
        builders.build_other(parser)
        return parser

    def __call__(self):
        matched = []
        non_matched = list(RULES)
        for path in Path().iterdir():
            for i, (match, _rule) in enumerate(non_matched):
                if fnmatch(path.name, match):
                    matched.append(non_matched.pop(i))
                    break

        matched = ['[{}]\n{}'.format(match, '\n'.join(rule)) for match, rule in matched]
        text = HEADER + '\n\n'.join(matched)
        Path('.editorconfig').write_text(text)
        self.logger.info('editorconfig generated')
        return True
