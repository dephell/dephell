try:
    from ruamel.yaml import YAML
    ruamel_yaml = YAML()
    ruamel_yaml_safe = YAML(typ='safe')
except ImportError:
    ruamel_yaml = None

try:
    import yaml as py_yaml
except ImportError:
    py_yaml = None

if py_yaml is None and ruamel_yaml is None:
    raise ImportError('please, install ruamel.yaml')


def yaml_load(stream, *, safe: bool = True):
    if ruamel_yaml is not None:
        try:
            if safe:
                return ruamel_yaml_safe.load(stream)
            return ruamel_yaml.load(stream)
        except Exception:
            # on error try to parse by PyYAML if available
            if py_yaml is not None:
                if safe:
                    return py_yaml.safe_load(stream)
                return py_yaml.load(stream)
            raise
    if py_yaml is not None:
        if safe:
            return py_yaml.safe_load(stream)
        return py_yaml.load(stream)
    raise RuntimeError('unreachable point reached')


def yaml_dump(data, stream):
    if ruamel_yaml is not None:
        return ruamel_yaml.dump(data, stream)
    if py_yaml is not None:
        return py_yaml.dump(data, stream)
    raise RuntimeError('unreachable point reached')
