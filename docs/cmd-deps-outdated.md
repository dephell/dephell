# dephell deps outdated

Show outdated project dependencies. It compares latest package version on [PyPI](https://pypi.org/) and version in the lockfile or project environment and shows packages that version is different.

Place to get dependencies from lookup:

1. If `to` format is a lockfile (`piplock`, `pipfilelock` or `poetrylock`) dependencies from this file will be used.
1. If `to` isn't specified and `from` is a lockfile dependencies from this file will be used.
1. Otherwise it uses common [Python environment lookup](python-lookup). TL;DR: project venv, current venv, python from config, python from dependencies file, current interpreter.

Some packages can have different version because their latest version incompatible with some other project dependencies, and DepHell's dependency resolver has locked their older (compatible) version. These packages also will be listed in the `dephell deps outdated` command output because explicit better than implicit.

This command returns non-zero code if some vulnerabilities was found, so you can use it on CI.

## Usage

Show all outdated packages:

```bash
$ dephell deps outdated

[
  {
    "description": "More routines for operating on iterables, beyond itertools",
    "installed": [
      "6.0.0"
    ],
    "latest": "7.0.0",
    "name": "more-itertools",
    "updated": "2019-03-28"
  },
  ...
]
```

[Filter](filters) only package name and latest release upload time:

```bash
$ dephell deps outdated --filter="#.name+updated.each()"
INFO get packages from project environment (path=/home/gram/.local/share/dephell/venvs/dephell-nLn6/main)
[
  {
    "name": "more-itertools",
    "updated": "2019-03-28"
  },
  ...
]
```

## See also

1. [How DepHell choose Python environment](python-lookup).
1. [How to filter commands JSON output](filters).
1. [dephell deps audit](cmd-deps-audit) to check dependencies for known vulnerabilities.
1. [dephell package list](cmd-package-list) to show information about installed packages.
1. [dephell package show](cmd-package-show) to get information about package.
1. [dephell venv create](cmd-venv-create) to create virtual environment for dependencies.
1. [dephell package install](cmd-package-install) to install a single package.
