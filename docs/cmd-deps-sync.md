# dephell deps sync

This command works in the same way as [dephell deps install](cmd-deps-install), but also removes from environment all packages that not presented in project dependencies (obsolete).

## See also

1. [How DepHell choose Python environment](python-lookup).
1. [dephell venv create](cmd-venv-create) to create virtual environment for dependencies.
1. [dephell deps install](cmd-deps-install) to install dependencies without dropping obsolete packages.
1. [dephell package install](cmd-package-install) to install single package.
1. [dephell jail install](cmd-package-install) to install some Python CLI tool into isolated virtual environment.
