import subprocess
from venv import create
from pathlib import Path

try:
    import pip  # noQA: F401
except ImportError:
    print('install pip')
    from ensurepip import bootstrap
    bootstrap()

try:
    from pip._internal import main
except ImportError:
    print('update pip')
    from ensurepip import bootstrap
    bootstrap(upgrade=True)


try:
    from appdirs import user_data_dir
except ImportError:
    print('install appdirs')
    main(['install', '--user', 'appdirs'])
    from appdirs import user_data_dir


print('make venv')
path = Path(user_data_dir('dephell')) / 'venvs' / 'dephell'
create(str(path), with_pip=True)


print('install dephell')
pip_path = list(path.glob('*/pip3'))[0]
exit(subprocess.run([str(pip_path), 'install', 'dephell[full]']))
