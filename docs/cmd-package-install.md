# dephell install

Install package. Looks for a place to install in the same way as [dephell deps install](cmd-deps-install):

1. If some virtual environment already active in the current shell then this environment will be used.
1. If virtual environment for current project (can be specified with `--config`) and environment (can be specified with `--env`) exists then this virtual environment will be used. This is the reason why you have to [create virtual environment](cmd-venv-create) before dependencies installation.
1. If virtual environment isn't found then your current python will be used.

```bash
$ dephell install pytest
```

Package specification the same as for [pip requirements file](https://pip.pypa.io/en/stable/reference/pip_install/#requirements-file-format):

```bash
$ dephell install requests[security]>=2.17.0
```

## See also

1. [dephell venv create](cmd-venv-create) for information about virtual environments management in DepHell.
1. [dephell deps install](cmd-deps-install) to install all project dependencies.
1. [dephell jail install](cmd-jail-install) to install Python CLI tools into isolated virtual environment.
