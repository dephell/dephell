# dephell package list

Show installed packages. If virtual environment for current project and environment exists this command will show packages for this virtual environment. Otherwise, this command will show all globally installed packages for current Python.

```bash
$ dephell package list
[
  {
    "authors": [
      "Hynek Schlawack",
      "Hynek Schlawack"
    ],
    "description": "Classes Without Boilerplate",
    "license": "MIT",
    "links": {
      "home": "https://www.attrs.org/",
      "project": "Documentation, https://www.attrs.org/"
    },
    "name": "attrs",
    "version": {
      "installed": [
        "19.1.0"
      ],
      "latest": "19.1.0"
    }
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

Show only name and description:

```bash
$ dephell package list --filter="#.name+description.each()"
[
  {
    "description": "Lightweight, extensible schema and data validation tool for Python dictionaries.",
    "name": "cerberus"
  },
  ...
]
```

Show name and description for first 10 packages (it can be useful for pagination by output):

```bash
$ dephell package list --filter="#.name+description.each().:10"
```

## See also

1. [How to filter commands JSON output](filters).
1. [dephell package install](cmd-package-install) to install package.
1. [dephell package search](cmd-package-search) to search packages on [PyPI](https://pypi.org/).
