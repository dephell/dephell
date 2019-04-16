# dephell package releases

Show available releases of package.

```bash
dephell package releases textdistance
[
  {
    "date": "2019-03-18",
    "python": "*",
    "version": "4.1.2"
  },
  ...
]
```

[Filter](filters) only versions:

```bash
dephell package releases --filter="#.version" textdistance
[
  "4.1.2",
  "4.1.1",
  "4.1.0",
  "4.0.0",
  "3.1.0",
  ...
]
```

Show 10 latest releases from git repository:

```bash
$ dephell package releases --filter=:10 git+https://github.com/orsinium/deal.git#egg=deal
[
  {
    "date": "2018-02-04",
    "python": "*",
    "version": "1.1.0"
  },
  ...
]
```

## See also

1. [How DepHell choose Python environment](python-lookup).
1. [How to filter commands JSON output](filters).
1. [dephell package search](cmd-package-search) to search packages on [PyPI](https://pypi.org/).
1. [dephell package show](cmd-package-list) to show information about package.
1. [dephell package install](cmd-package-install) to install package.
