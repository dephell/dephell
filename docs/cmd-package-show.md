# dephell package show

Show information about package by name.

```bash
$ dephell package show jsonschema
{
  "authors": [
    "Julian Berman <Julian@GrayVines.com>"
  ],
  "description": "An implementation of JSON Schema validation for Python",
  "installed": [
    "2.6.0",
    "3.0.1"
  ],
  "latest": "3.0.1",
  "license": "MIT",
  "links": {
    "homepage": "https://github.com/Julian/jsonschema",
    "package": "https://pypi.org/project/jsonschema/"
  },
  "locations": [
    "/home/gram/.local/lib/python3.7/site-packages/jsonschema",
    "/usr/local/lib/python3.7/site-packages/jsonschema"
  ],
  "name": "jsonschema",
  "size": "620.11Kb",
  "updated": "2019-03-01"
}
```

If virtual environment for current project and environment exists this command will get package version for this virtual environment. Otherwise, this command will get package versions from all paths from `sys.path` for current Python. This is the reason why `version.installed` is a list.

## Conda (Anaconda Cloud and conda-forge recipes)

By default, this command uses information from [PyPI](http://pypi.org). However, you can explicitly specify `--repo` to search package among conda recipes.

Search recipes in the [conda-froge](https://github.com/conda-forge/) Github repository:

```bash
$ dephell package show --repo=conda_git make
{
  "authors": [],
  "description": "GNU Make is a tool which controls the generation of executables and other non-source files of a program from the program's source files.",
  "latest": "4.2.1",
  "license": "GPLv3",
  "links": {
    "documentation": "https://www.gnu.org/software/make/manual/",
    "homepage": "https://www.gnu.org/software/make/"
  },
  "name": "make",
  "updated": "2019-01-12"
}
```

Search builded packages in [Anaconda Cloud](https://anaconda.org/) (provides less info, works slower):

```bash
$ dephell package show --repo=conda_cloud make
{
  "authors": [],
  "description": "",
  "latest": "4.2.1",
  "license": "GPLv3",
  "links": {
    "anaconda": "https://anaconda.org/defaults/make"
  },
  "name": "make",
  "updated": "2018-04-04"
}
```


## See also

1. [How DepHell choose Python environment](python-lookup).
1. [How to filter commands JSON output](filters).
1. [dephell package search](cmd-package-search) to search packages.
1. [dephell package list](cmd-package-list) to show information about installed packages.
1. [dephell package install](cmd-package-install) to install package.
