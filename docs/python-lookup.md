# Python and venv lookup

Some commands try to find out the best venv to get information about packages or the best python executable to install packages or create venv. There is described lookup order for these commands.

## Python interpreter lookup

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

## Virtual environment (venv) lookup

1. If virtual environment for current project (can be specified with `--config`) and environment (can be specified with `--env`) exists then this virtual environment will be used. This is the reason why you have to [create virtual environment](cmd-venv-create) before dependencies installation. Can be overwritten by `--venv` parameter.
2. If some venv is active then it will be used.

This lookup is used in command [dephell inspect venv](cmd-inspect-venv).

## Python environment

Python environment -- any python interpreter: virtual environment or globally installed interpreter. This lookup used when DepHell looks for place to work with packages (analyze, install, remove).

1. First of all, DepHell tries to find virtual environment by virtual environment lookup.
1. If there is no virtual environment then DepHell looks for best global interpreter by Python interpreter lookup.

Commands that use this lookup:

+ [dephell deps install](cmd-deps-install)
+ [dephell deps outdated](cmd-deps-outdated)
+ [dephell package install](cmd-package-install)
+ [dephell package list](cmd-package-list)
+ [dephell package show](cmd-package-show)
