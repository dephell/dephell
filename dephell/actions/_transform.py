from bowler import LN, Capture, Filename, Query
from bowler.helpers import power_parts, quoted_parts, dotted_parts
from fissix.pytree import Node, Leaf
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
    """import foo -> import foo as bar
    """

    selector = """
        import_name< 'import'
            (
                module_name='{name}'
            |
                module_name=dotted_name< {dotted_name} any* >
            |
                dotted_as_name<
                    (
                        module_name='{name}'
                    |
                        module_name=dotted_name< {dotted_name} any* >
                    )
                    'as' module_nickname=any
                >
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
        print(old_leaf)
        old_leaf.replace(new_node)
        print(old_leaf)
