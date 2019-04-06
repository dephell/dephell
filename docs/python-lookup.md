# Python and venv lookup

Some commands try to find out the best venv to get information about packages or the best python executable to install packages or create venv. There is described lookup order for these commands.

## Python lookup

1. `python` parameter in the [config](config) (or as CLI argument `--python`, of course). You can define python here in any way as you want:
    1. Version (`3.7`)
    1. Exact version (`3.7.2`)
    1. Constraint (`>=3.5`)
    1. Executable name (`python3`)
    1. Path to the executable (`/usr/bin/python3`)
1. Dependencies file defined in `from` parameter. For example, [python_requires](https://packaging.python.org/guides/distributing-packages-using-setuptools/#python-requires) from setup.py.
1. If nothing was found current interpreter (that runs DepHell) will be used.

This lookup is used in commands that can create virtual environment:

+ [dephell jail install](cmd-jail-install)
+ [dephell venv create](cmd-venv-create)
+ [dephell venv run](cmd-venv-run)
+ [dephell venv shell](cmd-venv-shell)

## Venv lookup

1. Venv for current project and env.
2. Current active venv.
