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
result = subprocess.run([str(pip_path), 'install', 'dephell[full]'])
if result.returncode != 0:
    exit(result.returncode)

print('copy binary dephell')
local_path = pip_path.parent / 'dephell'
if not local_path.exists():
    print('DepHell binary not found')
    exit(1)
global_path = Path.home() / '.local' / 'bin' / 'dephell'
if global_path.exists() or global_path.is_symlink():
    global_path.unlink()
global_path.symlink_to(local_path)
