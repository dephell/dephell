from bowler import LN, Capture, Filename, Query
from bowler.helpers import power_parts, quoted_parts, dotted_parts
from fissix.pytree import Node, Leaf
from fissix.pgen2 import token
from fissix.fixer_util import syms, Name, Dot


modifiers = []


def _register(modifier):
    modifiers.append(modifier)
    return modifier


def transform_imports(query: Query, old_name: str, new_name: str) -> Query:
    params = dict(
        name=old_name,
        dotted_name=' '.join(quoted_parts(old_name)),
        power_name=' '.join(power_parts(old_name)),
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
            |
                module_name=dotted_name< {dotted_name} any* >
            )
        >
        """

    def __init__(self, old_name, new_name):
        self.old_name = old_name
        self.new_name = new_name

    def __call__(self, node: LN, capture: Capture, filename: Filename) -> None:
        if capture['node'].type != syms.import_name:
            return
        if type(capture['module_name']) is Node:
            module_name = ''.join(child.value for child in capture['module_name'].children)
        else:
            module_name = capture['module_name'].value
        if module_name == self.old_name:
            self._modify(capture['node'])

    def _modify(self, node: Node):
        if '.' in self.old_name:
            children = []
            for part in dotted_parts(self.old_name):
                if part == '.':
                    children.append(Dot())
                else:
                    children.append(Name(part))
            old_name_node = Node(
                type=syms.dotted_name,
                children=children,
            )
        else:
            old_name_node = Name(self.old_name, prefix=' ')

        if node.children[1].type == syms.dotted_as_names:
            for child in node.children[1].children:
                if child.type == token.NAME and child.value == self.old_name:
                    old_leaf = child
                    break
            else:
                raise RuntimeError('cannot find given module')
        else:
            old_leaf = node.children[1]

        new_node = Node(
            type=syms.dotted_as_name,
            children=[
                Leaf(
                    type=old_leaf.type,
                    value=self.new_name,
                    prefix=old_leaf.prefix,
                ),
                Name('as', prefix=' '),
                old_name_node,
            ],
        )
        old_leaf.replace(new_node)


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

    def __init__(self, old_name, new_name):
        self.old_name = old_name
        self.new_name = new_name

    def __call__(self, node: LN, capture: Capture, filename: Filename) -> None:
        if capture['node'].type != syms.import_from:
            return

        # build given module name from nodes
        if type(capture['module_name']) is Node:
            module_name = ''.join(child.value for child in capture['module_name'].children)
        else:
            module_name = capture['module_name'].value

        # modify module name if it's old_name module or import from old_name module
        if module_name == self.old_name:
            self._modify(capture['node'])
        elif module_name.startswith(self.old_name + '.'):
            self._modify(capture['node'])

    def _modify(self, node: Node):
        old_name_node = node.children[1]
        new_name_node = _build_new_name_node(
            old_name_node=old_name_node,
            new_name=self.new_name,
            old_name=self.old_name,
            attach=True,
        )
        old_name_node.replace(new_name_node)


@_register
class ModuleAsImportModifier:
    """import foo as bar -> import baz as bar
    """

    selector = """
        import_name< 'import'
            dotted_as_name<
                (
                    module_name='{name}'
                |
                    module_name=dotted_name< {dotted_name} any* >
                )
                'as' module_nickname=any
            >
        >
        """

    def __init__(self, old_name, new_name):
        self.old_name = old_name
        self.new_name = new_name

    def __call__(self, node: LN, capture: Capture, filename: Filename) -> None:
        if capture['node'].type != syms.import_name:
            return
        if type(capture['module_name']) is Node:
            module_name = ''.join(child.value for child in capture['module_name'].children)
        else:
            module_name = capture['module_name'].value

        if module_name == self.old_name:
            self._modify(capture['node'])
        elif module_name.startswith(self.old_name + '.'):
            self._modify(capture['node'])

    def _modify(self, node: Node):
        old_name_node = node.children[1].children[0]
        new_name_node = _build_new_name_node(
            old_name_node=old_name_node,
            new_name=self.new_name,
            old_name=self.old_name,
            attach=True,
        )
        old_name_node.replace(new_name_node)


def _build_new_name_node(old_name_node, new_name: str, old_name: str, attach: bool):
    # build new node from new_name
    if '.' in new_name:
        children = []
        for part in dotted_parts(new_name):
            if part == '.':
                children.append(Dot())
            else:
                children.append(Name(part))
    else:
        children = [Name(new_name)]

    # attach to the new node subimports from the old module
    if attach and type(old_name_node) is Node:
        original_name_size = len(dotted_parts(old_name))
        for part in old_name_node.children[original_name_size:]:
            if part.value == '.':
                children.append(Dot())
            else:
                children.append(Name(part.value))

    return Node(
        type=syms.dotted_name,
        children=children,
        prefix=old_name_node.prefix,
    )
