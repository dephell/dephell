# dephell package list

Show installed packages. See [how DepHell looks for Python environment](python-lookup).

```bash
$ dephell package list
[
  {
    "authors": [
      "Hynek Schlawack",
      "Hynek Schlawack"
    ],
    "description": "Classes Without Boilerplate",
    "installed": [
      "19.1.0"
    ],
    "latest": "19.1.0"
    "license": "MIT",
    "links": {
      "home": "https://www.attrs.org/",
      "project": "Documentation, https://www.attrs.org/"
    },
    "name": "attrs",
  },
  ...
]
```

Output of this command is really long. So, in most cases you want to [filter it](filters).

Show only names:

```bash
dephell package list --filter="#.name.sorted()"
[
  "aiofiles",
  "aiohttp",
  "appdirs",
  ...
]
```

Show only name and installed versions:

```bash
$ dephell package list --filter="#.name+installed.each()"
[
  {
    "installed": [
      "1.2"
    ],
    "name": "cerberus"
  },
  ...
]
```

Show name and description for first 10 packages (it can be useful for pagination by output):

```bash
$ dephell package list --filter="#.name+description.each().:10"
[
  {
    "description": "Lightweight, extensible schema and data validation tool for Python dictionaries.",
    "name": "cerberus"
  },
  ...
]
```

## See also

1. [How DepHell choose Python environment](python-lookup).
1. [How to filter commands JSON output](filters).
1. [dephell deps outdated](cmd-deps-outdated) to show outdated packages in the virtual environment or lockfile.
1. [dephell package search](cmd-package-search) to search packages on [PyPI](https://pypi.org/).
1. [dephell package show](cmd-package-show) to get information about single package.
1. [dephell package install](cmd-package-install) to install package.
