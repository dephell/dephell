# dephell package bug

Report bug in a package. The command finds a bug tracker, associated with the package, and opens the tracker URL in a new browser tab.

```bash
$ dephell package bug flask
```

Packages in Conda also supported:

```bash
$ dephell package bug --repo conda textdistance
```

## See also

1. [dephell package changelog](cmd-package-changelog) to find changelog for a package or release.
1. [dephell package show](cmd-package-show) to get information about package.
1. [dephell package search](cmd-package-search) to search packages on [PyPI](https://pypi.org/).
