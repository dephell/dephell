# dephell deps check

Show difference between virtual environment and project dependencies.

```bash
dephell deps check
INFO get dependencies (format=setuppy, path=setup.py)
INFO build dependencies graph...
[
  {
    "action": "remove",
    "installed": "2.2.1",
    "locked": null,
    "name": "deal"
  }
]
```

Fields:

+ `action` -- what would happened if you run [dephell deps sync](cmd-deps-sync). Can be `install`, `update` or `remove`.
+ `name` -- package name (wow!).
+ `installed` -- installed version of a package. `null` if a package isn't installed.
+ `locked` -- version of a package in the dependencies graph or locked by resolver. `null` if a package isn't represented in dependencies graph.

## See also

1. [How DepHell choose Python environment](python-lookup).
1. [dephell deps install](cmd-deps-install) to install project dependencies.
1. [dephell venv create](cmd-venv-create) to create virtual environment for dependencies.
1. [dephell package install](cmd-package-install) to install single package
1. [dephell jail install](cmd-package-install) to install some Python CLI tool into isolated virtual environment.
