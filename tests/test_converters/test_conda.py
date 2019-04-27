# project
# from dephell.controllers import DependencyMaker
from dephell.converters.conda import CondaConverter
# from dephell.models import Requirement, RootDependency


def test_conda_loads():
    content = '\n'.join([
        'name: deeplearning',
        'channels:',
        '- defaults',
        '- conda-forge',
        'dependencies:',
        '- python=3.6',
        '- matplotlib=2.0.2',
        '- numpy',
    ])
    root = CondaConverter().loads(content=content)
    assert str(root.name) == 'deeplearning'
    assert str(root.python) == '==3.6.*'
    deps = {dep.name: str(dep.constraint) for dep in root.dependencies}
    assert deps == {'matplotlib': '==2.0.2', 'numpy': '*'}
