

class Operation:
    op = ''

    def __init__(self, *nodes):
        new_nodes = []
        for node in nodes:
            if isinstance(node, type(self)):
                # get nodes from child node if this node has the same type
                new_nodes.extend(node.nodes)
            else:
                # if this is single marker or other Operation then just append
                new_nodes.append(node)
        self.nodes = new_nodes

    def __str__(self):
        sep = ' ' + self.op + ' '
        return '(' + sep.join(map(str, self.nodes)) + ')'

    def __repr__(self):
        return '{}({})'.format(
            type(self).__name__,
            ', '.join(map(repr, self.nodes)),
        )
