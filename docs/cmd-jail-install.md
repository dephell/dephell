# dephell jail install

Install package into isolated virtual environment. It works similar to [pipsi](https://github.com/mitsuhiko/pipsi), but with DepHell magic:

1. Creates virtual environment named after package to install.
1. Resolves package dependencies.
1. Installs package and dependencies.
1. Creates symlinks for package entrypoints.

Like [dephell package install](cmd-package-install), it can parse any [pip-compatible input](https://pip.pypa.io/en/stable/reference/pip_install/#requirements-file-format). For example:

```bash
$ dephell jail install isort[requirements,pipfile]
```

It will install [isort](https://github.com/timothycrosley/isort) with [requirements.txt](https://pip.pypa.io/en/stable/user_guide/#requirements-files) and [Pipfile](https://github.com/pypa/pipfile) support in the isolated virtual environment named `isort`.

## See also

1. [dephell jail list](cmd-jail-list) to show all created jails.
1. [dephell jail remove](cmd-jail-remove) to remove jail.
1. [dephell venv create](cmd-venv-create) for information about virtual environments management in DepHell.
1. [dephell package install](cmd-package-install) to install package into project virtual environment.
1. [dephell deps install](cmd-deps-install) to install all project dependencies.
