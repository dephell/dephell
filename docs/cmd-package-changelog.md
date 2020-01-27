# dephell package changelog

Find changelog for a package or release.

For package:

```bash
dephell package changelog pytest
```

For releases:

```bash
dephell package changelog pytest 3.0.7 3.0.6
```

The changelog will be printed as-is, with original grammar. So, you can redirect it into a file to render it then with an external tool:

```bash
dephell package changelog pytest > pytest_changelog.rst
```

The current implementation works for 80% cases. The changelog must be in one file and uploaded in the GitHub repository of the project.

## See also

1. [dephell package bug](cmd-package-bug) to find bugtracker for a package.
1. [dephell package show](cmd-package-show) to get information about package.
1. [dephell package search](cmd-package-search) to search packages on [PyPI](https://pypi.org/).
