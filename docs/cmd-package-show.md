# dephell package show

Show information about package by name.

```bash
$ dephell package show jsonschema
{
  "authors": [
    "Julian Berman <Julian@GrayVines.com>"
  ],
  "description": "An implementation of JSON Schema validation for Python",
  "license": "MIT",
  "links": {
    "homepage": "https://github.com/Julian/jsonschema",
    "package": "https://pypi.org/project/jsonschema/"
  },
  "name": "jsonschema",
  "updated": "2019-03-01",
  "version": {
    "installed": [
      "2.6.0",
      "3.0.1"
    ],
    "latest": "3.0.1"
  }
}
```

If virtual environment for current project and environment exists this command will get package version for this virtual environment. Otherwise, this command will get package versions from all paths from `sys.path` for current Python. This is the reason why `version.installed` is a list.

If you want to find package location on your system use [locate](https://alvinalexander.com/blog/post/linux-unix/use-linux-locate-command):

```bash
$ locate jsonschema/__init__.py
/home/gram/.local/lib/python3.5/site-packages/jsonschema/__init__.py
/home/gram/.local/lib/python3.7/site-packages/jsonschema/__init__.py
/usr/local/lib/python3.7/site-packages/jsonschema/__init__.py
```

## See also

1. [How to filter commands JSON output](filters).
1. [dephell package search](cmd-package-search) to search packages on [PyPI](https://pypi.org/).
1. [dephell package list](cmd-package-list) to show information about installed packages.
1. [dephell package install](cmd-package-install) to install package.
