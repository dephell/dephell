

def to_requirements(graph):
    deps = []
    for dep in graph.mapping.values():
        deps.append(str(dep.group.best_release))
    return '\n'.join(deps)
