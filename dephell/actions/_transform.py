# built-in
from typing import TYPE_CHECKING

# app
from ..imports import lazy_import


bowler_helpers = lazy_import('bowler.helpers')
fissix_pytree = lazy_import('fissix.pytree')
fixer_util = lazy_import('fissix.fixer_util')


if TYPE_CHECKING:
    from bowler import LN, Capture, Filename, Query


modifiers = []


def _register(modifier: type) -> type:
    modifiers.append(modifier)
    return modifier


def transform_imports(query: 'Query', old_name: str, new_name: str) -> 'Query':
    params = dict(
        name=old_name,
        dotted_name=' '.join(bowler_helpers.quoted_parts(old_name)),
        power_name=' '.join(bowler_helpers.power_parts(old_name)),
    )
    for modifier_class in modifiers:
        modifier = modifier_class(old_name=old_name, new_name=new_name)
        selector = modifier.selector.format(**params)
        query = query.select(selector).modify(modifier)

    return query


@_register
class ModuleImportModifier:
    """import foo -> import bar as foo
    """

    selector = """
        import_name< 'import'
            (
                module_name='{name}' any*
            |
                dotted_as_names< (any ',')* module_name='{name}' (',' any)* >
            )
        >
        """

    def __init__(self, old_name: str, new_name: str) -> None:
        self.old_name = old_name
        self.new_name = new_name

    def __call__(self, node: 'LN', capture: 'Capture', filename: 'Filename') -> None:
        old_node = capture['module_name']
        new_node = fissix_pytree.Node(
            type=fixer_util.syms.dotted_as_name,
            children=[
                build_new_name_node(
                    old_node=old_node,
                    new_name=self.new_name,
                    attach=False,
                ),
                fixer_util.Name('as', prefix=' '),
                old_node.clone(),
            ],
        )
        old_node.replace(new_node)


@_register
class FromImportModifier:
    """import foo -> import bar as foo
    """

    selector = """
        import_from< 'from'
            (
                module_name='{name}'
            |
                module_name=dotted_name< {dotted_name} any* >
            )
            'import' any*
        >
        """

    def __init__(self, old_name: str, new_name: str) -> None:
        self.old_name = old_name
        self.new_name = new_name

    def __call__(self, node: 'LN', capture: 'Capture', filename: 'Filename') -> None:
        new_name_node = build_new_name_node(
            old_node=capture['module_name'],
            new_name=self.new_name,
            old_name=self.old_name,
            attach=True,
        )
        capture['module_name'].replace(new_name_node)


@_register
class ModuleAsImportModifier:
    """import foo as bar -> import baz as bar
    """

    selector = """
        import_name< 'import'
            (
                dotted_as_name<
                    (
                        module_name='{name}'
                    |
                        module_name=dotted_name< {dotted_name} any* >
                    )
                    'as' module_nickname=any
                >
            |
                dotted_as_names<
                    (any ',')*
                    dotted_as_name<
                        (
                            module_name='{name}'
                        |
                            module_name=dotted_name< {dotted_name} any* >
                        )
                        'as' module_nickname=any
                    >
                    (',' any)*
                >
            )
        >
        """

    def __init__(self, old_name: str, new_name: str) -> None:
        self.old_name = old_name
        self.new_name = new_name

    def __call__(self, node: 'LN', capture: 'Capture', filename: 'Filename') -> None:
        new_name_node = build_new_name_node(
            old_node=capture['module_name'],
            new_name=self.new_name,
            old_name=self.old_name,
            attach=True,
        )
        capture['module_name'].replace(new_name_node)


@_register
class StringModifier:
    """sys.modules["foo"] -> sys.modules["bar"]
    """

    selector = """
        string=STRING
        """

    def __init__(self, old_name: str, new_name: str) -> None:
        self.old_name = old_name
        self.new_name = new_name

    def __call__(self, node: 'LN', capture: 'Capture', filename: 'Filename') -> None:
        if not self._capture(capture['string'].value):
            return

        old_node = capture['string']
        new_node = old_node.clone()
        new_node.value = old_node.value.replace(self.old_name, self.new_name)
        old_node.replace(new_node)

    def _capture(self, value):
        if value[0] in 'uUrRbBfF':
            value = value[1:]
        for quote in ('"', "'"):
            if value.strip(quote) == self.old_name:
                return True
            if value.strip(quote).startswith(self.old_name + '.'):
                return True
        return False


# @_register
class DottedModuleImportModifier:
    """import foo.bar -> import baz.bar
    """

    selector = """
        (
            import_name< 'import' module_name=dotted_name< {dotted_name} any* > >
        |
            power< {power_name} any* >
        )
        """

    def __init__(self, old_name: str, new_name: str) -> None:
        self.old_name = old_name
        self.new_name = new_name

    def __call__(self, node: 'LN', capture: 'Capture', filename: 'Filename') -> None:
        if node.type == fixer_util.syms.power:
            self._modify_power(node)
        else:
            self._modify_import(capture)

    def _modify_import(self, capture) -> None:
        new_name_node = build_new_name_node(
            old_node=capture['module_name'],
            new_name=self.new_name,
            old_name=self.old_name,
            attach=True,
        )
        capture['module_name'].replace(new_name_node)

    def _modify_power(self, node: 'LN') -> None:
        prefix = node.children[0].prefix

        # remove old prefix
        parts = bowler_helpers.dotted_parts(self.old_name)
        for _ in range((len(parts) + 1) // 2):
            node.children.pop(0)

        # add new prefix
        name = self.new_name.split('.', maxsplit=1)[0]
        head = fixer_util.Name(name, prefix=prefix)
        children = []
        for part in bowler_helpers.dotted_parts(self.new_name)[2::2]:
            children.append(fissix_pytree.Node(
                type=fixer_util.syms.trailer,
                children=[fixer_util.Dot(), fixer_util.Name(part)],
            ))
        node.children = [head] + children + node.children


def build_new_name_node(*, old_node, attach: bool, new_name: str, old_name: str = None):
    # build new node from new_name
    if '.' in new_name:
        children = []
        for part in bowler_helpers.dotted_parts(new_name):
            if part == '.':
                children.append(fixer_util.Dot())
            else:
                children.append(fixer_util.Name(part))
    else:
        children = [fixer_util.Name(new_name)]

    # attach to the new node subimports from the old module
    if attach and type(old_node) is fissix_pytree.Node:
        original_name_size = len(bowler_helpers.dotted_parts(old_name))
        for part in old_node.children[original_name_size:]:
            if part.value == '.':
                children.append(fixer_util.Dot())
            else:
                children.append(fixer_util.Name(part.value))

    return fissix_pytree.Node(
        type=fixer_util.syms.dotted_name,
        children=children,
        prefix=old_node.prefix,
    )
