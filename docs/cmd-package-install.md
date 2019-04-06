# dephell package install

Install package. See [how DepHell looks for Python environment](python-lookup).

```bash
$ dephell package install pytest
```

Package specification the same as for [pip requirements file](https://pip.pypa.io/en/stable/reference/pip_install/#requirements-file-format):

```bash
$ dephell package install requests[security]>=2.17.0
```

## See also

1. [How DepHell choose Python environment](python-lookup).
1. [dephell venv create](cmd-venv-create) for information about virtual environments management in DepHell.
1. [dephell deps install](cmd-deps-install) to install all project dependencies.
1. [dephell jail install](cmd-jail-install) to install Python CLI tools into isolated virtual environment.
