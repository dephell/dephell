# dephell deps install

Install project dependencies.

Dependencies from `to` option will be used if available. This is because when you specified in config file source dependencies in `from` and locked dependencies in `to` then, of course, you want to install dependencies from lock file. However, if `to` (and `to-format` and `to-file`) isn't specified in the config and CLI arguments then `from` will be used.

Place to install lookup:

1. If some virtual environment already active in the current shell then this environment will be used.
1. If virtual environment for current project (can be specified with `--config`) and environment (can be specified with `--env`) exists then this virtual environment will be used. This is the reason why you have to [create virtual environment](cmd-venv-create) before dependencies installation.
1. If virtual environment isn't found then your current python will be used.

## See also

1. [dephell venv create](cmd-venv-create) to create virtual environment for dependencies.
1. [dephell install](cmd-install) to install single package
1. [dephell jail install](cmd-install) to install some Python CLI tool into isolated virtual environment.
