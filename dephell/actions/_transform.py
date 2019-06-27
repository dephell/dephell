from bowler import LN, Capture, Filename, Query
from bowler.helpers import power_parts, quoted_parts
from fissix.pytree import Node, Leaf
from fissix.fixer_util import syms, Name


MODULE_IMPORT_SELECTOR = """
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


def transform_as_import(query: Query, old_name: str, new_name: str) -> Query:
    modifier = AsImportModifier(old_name=old_name, new_name=new_name)
    selector = MODULE_IMPORT_SELECTOR.format(
        name=old_name,
        dotted_name=' '.join(quoted_parts(old_name)),
        power_name=' '.join(power_parts(old_name)),
    )
    return query.select(selector).modify(modifier)


class AsImportModifier:
    def __init__(self, old_name, new_name):
        self.old_name = old_name
        self.new_name = new_name

    def __call__(self, node: LN, capture: Capture, filename: Filename) -> None:
        if capture['node'].type == syms.import_name:
            if capture['module_name'].value == self.old_name:
                self._modify_to_as(capture['node'])

    def _modify_to_as(self, node: Node):
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
                Name(self.old_name, prefix=' '),
            ],
        )
        old_leaf.replace(new_node)
