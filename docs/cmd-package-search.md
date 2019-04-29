# dephell package search

Search packages on [PyPI](https://pypi.org/) or [Anaconda Cloud](https://docs.anaconda.com/anaconda-cloud/).

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

## Anaconda Cloud

A few differences from search on PyPI:

1. Specify `--repo=conda` to search on Anaconda Cloud.
1. Search text (text without query filters) is required.
1. Available query filters:
    1. `type` (`conda`, `pypi`, `env`, `ipynb`)
    1. `platform` (`osx-32`, `osx-64`, `win-32`, `win-64`, `linux-32`, `linux-64`, `linux-armv6l`, `linux-armv7l`, `linux-ppc64le`, `noarch`)
1. Results also contain fields `links`, `license`, and `channel`.

Examples:

```bash
$ dephell package search --repo=conda textdistance
[
  {
    "channel": "conda-forge",
    "description": "TextDistance – python library for comparing distance between two or more sequences by many algorithms.",
    "license": "LGPL-3.0",
    "links": {
      "anaconda": "http://anaconda.org/conda-forge/textdistance",
      "documentation": "https://pypi.org/project/textdistance/#description",
      "homepage": "https://github.com/orsinium/textdistance",
      "repository": "https://github.com/orsinium/textdistance"
    },
    "name": "textdistance",
    "version": "4.1.0"
  }
]
```

```bash
dephell package search --repo=conda --filter=":5" keras type:ipynb
[
  {
    "channel": "zenlambda",
    "description": "IPython notebook",
    "license": {},
    "links": {
      "anaconda": "http://anaconda.org/zenlambda/keras"
    },
    "name": "keras",
    "version": "2017.02.26.2159"
  },
  ...
]
```

## See also

1. [How to filter commands JSON output](filters).
1. [dephell package show](cmd-package-search) to show information about single package.
1. [dephell package list](cmd-package-list) to show information about installed packages.
1. [dephell package install](cmd-package-install) to install package.
