from packaging.version import LegacyVersion, parse
from packaging.specifiers import SpecifierSet, LegacySpecifier


def check_spec(version: str, spec: str):
    """
    https://www.python.org/dev/peps/pep-0440/
    """
    if not spec:
        return True
    spec = SpecifierSet(str(spec))
    version = parse(version)

    # check semantic version
    if not isinstance(version, LegacyVersion):
        return version in spec

    # check legacy version
    for subspec in str(spec).split(','):
        subspec = LegacySpecifier(subspec)
        if version not in subspec:
            return False
    return True
