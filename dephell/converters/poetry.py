from tomlkit import document, dumps


def from_poetry(path):
    ...


def to_poetry(graph):
    doc = document()
    ...
    return dumps(doc)
