# dephell package purge

Remove package with package dependencies:

```bash
$ dephell package purge tomlkit
```

This command removes package and package dependencies that aren't required for other packages in the environment. For example, you want to remove `pathlib2`. This package has `scandir` and `six` in the requirements. However, `six` also used in `requests`, that also installed on your system. `scandir` isn't used in another package. So, this command will remove only `pathlib2` and `scandir`. Of course, `scandir` can be used in some of your projects that isn't explicitly installed. So, if you want to avoid it and drop only package without dependencies use [dephell package remove](cmd-package-remove).

## See also

1. [How DepHell choose Python environment](python-lookup).
1. [dephell package remove](cmd-package-remove) to remove package without dependencies.
1. [dephell package install](cmd-package-install) to install package into environment.
1. [dephell deps install](cmd-deps-install) to install all project dependencies.
1. [dephell jail install](cmd-jail-install) to install Python CLI tools into isolated virtual environment.
