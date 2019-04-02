# dephell package search

Search packages on [PyPI](https://pypi.org/).

## Simple search by name

```bash
dephell package search dephell
[
  {
    "description": "Dependency resolution for Python",
    "name": "dephell",
    "url": "https://pypi.org/project/dephell/",
    "version": "0.3.1"
  },
  {
    "description": "Work with python versions",
    "name": "dephell-pythons",
    "url": "https://pypi.org/project/dephell-pythons/",
    "version": "0.1.0"
  },
  ...
]
```

## Query filters

Supported query filters:

+ author_email
+ author
+ description
+ download_url
+ home_page
+ keywords
+ license
+ maintainer_email
+ maintainer
+ name
+ platform
+ summary
+ version

Get all projects of author:

```bash
$ dephell package search author:orsinium
[
  {
    "description": "Find project modules and data files (packages and package_data for setup.py).",
    "name": "dephell-discover",
    "url": "https://pypi.org/project/dephell-discover/",
    "version": "0.1.0"
  },
  ...
]
```

Or get first 10 packages with "environment markers" in the summary:

```bash
$ dephell package search --filter=":10" summary:"environment markers"
[
  {
    "description": "A compiler for PEP 345 environment markers.",
    "name": "markerlib",
    "url": "https://pypi.org/project/markerlib/",
    "version": "0.6.0"
  },
  {
    "description": "Work with environment markers (PEP-496)",
    "name": "dephell-markers",
    "url": "https://pypi.org/project/dephell-markers/",
    "version": "0.2.3"
  },
  ...
]
```

You can combine any query filters together:

```bash
$ dephell package search author:orsinium name:dephell
```

## See also

1. [How to filter commands JSON output](filters).
1. [dephell package show](cmd-package-search) to show information about single package.
1. [dephell package list](cmd-package-list) to show information about installed packages.
1. [dephell package install](cmd-package-install) to install package.
