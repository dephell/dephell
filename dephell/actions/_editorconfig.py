# built-in
from pathlib import Path
from typing import Tuple

# external
import attr


@attr.s(frozen=True)
class Rule:
    header = attr.ib(type=str)
    patterns = attr.ib(type=Tuple[str, ...])
    styles = attr.ib(type=Tuple[str, ...])

    def match(self, path: Path) -> bool:
        for pattern in self.patterns:
            iterator = path.glob(pattern)
            try:
                next(iterator)
            except StopIteration:
                continue
            return True
        return False

    def __str__(self) -> str:
        return '[{header}]\n{styles}'.format(
            header=self.header,
            styles='\n'.join(self.styles),
        )


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
    # 4 spaces
    Rule(
        header='*.py',
        patterns=('**/*.py', ),
        styles=('indent_style = space', 'indent_size = 4'),
    ),
    Rule(
        header='*.{md,rst,txt}',
        patterns=('*.md', '*.rst', '*.txt'),
        styles=('indent_style = space', 'indent_size = 4'),
    ),
    Rule(
        header='*.{ini,toml}',
        patterns=('*.ini', '*.toml'),
        styles=('indent_style = space', 'indent_size = 4'),
    ),
    Rule(
        header='*Dockerfile',
        patterns=('*.Dockerfile', 'Dockerfile'),
        styles=('indent_style = space', 'indent_size = 4'),
    ),

    # 2 spaces
    Rule(
        header='*.js',
        patterns=('**/*.js', ),
        styles=('indent_style = space', 'indent_size = 2'),
    ),
    Rule(
        header='*.{json,yml,yaml}',
        patterns=('*.json', '*.yml', '*.yaml'),
        styles=('indent_style = space', 'indent_size = 2'),
    ),
    Rule(
        header='*.{html,html.j2}',
        patterns=('**/*.html', '**/*.html.j2'),
        styles=('indent_style = space', 'indent_size = 2'),
    ),

    # tabs
    Rule(
        header='Makefile',
        patterns=('Makefile', ),
        styles=('indent_style = tab', ),
    ),
    Rule(
        header='*.go',
        patterns=('*.go', ),
        styles=('indent_style = tab', ),
    ),
)


def make_editorconfig(path: Path) -> str:
    matched = []
    non_matched = []
    for rule in RULES:
        if rule.match(path):
            matched.append(rule)
        else:
            non_matched.append(rule)

    return HEADER + '\n\n'.join(map(str, matched)) + '\n'
