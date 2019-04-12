# ![DepHell](./assets/logo.png)

[![MIT License](https://img.shields.io/pypi/l/dephell.svg)](https://github.com/dephell/dephell/blob/master/LICENSE)
[![Powered by DepHell](./assets/badge.svg)](./docs/badge.md)

**DepHell** -- dependency management for Python.

+ Manage dependencies: [convert between formats](https://dephell.readthedocs.io/en/latest/cmd-deps-convert.html), [install](https://dephell.readthedocs.io/en/latest/cmd-deps-install.html), lock, [add new](https://dephell.readthedocs.io/en/latest/cmd-deps-add.html), resolve conflicts.
+ Manage virtual environments: [create](https://dephell.readthedocs.io/en/latest/cmd-venv-create.html), [remove](https://dephell.readthedocs.io/en/latest/cmd-venv-destroy.html), [inspect](https://dephell.readthedocs.io/en/latest/cmd-inspect-venv.html), [run shell](https://dephell.readthedocs.io/en/latest/cmd-venv-shell.html), [run commands inside](https://dephell.readthedocs.io/en/latest/cmd-venv-run.html).
+ [Install CLI tools](https://dephell.readthedocs.io/en/latest/cmd-jail-install.html) into isolated environments.
+ Manage packages: [install](https://dephell.readthedocs.io/en/latest/cmd-package-install.html), [list](https://dephell.readthedocs.io/en/latest/cmd-package-list.html), [search](https://dephell.readthedocs.io/en/latest/cmd-package-search.html) on PyPI.
+ [Build](https://dephell.readthedocs.io/en/latest/cmd-project-build.html) packages (to upload on PyPI), [test](https://dephell.readthedocs.io/en/latest/cmd-project-test.html), [bump project version](https://dephell.readthedocs.io/en/latest/cmd-project-bump.html).
+ [Discover licenses](https://dephell.readthedocs.io/en/latest/cmd-deps-licenses.html) of all project dependencies, show [outdated](https://dephell.readthedocs.io/en/latest/cmd-deps-outdated.html) packages, [find security issues](https://dephell.readthedocs.io/en/latest/cmd-deps-audit.html).
+ Generate [.editorconfig](https://dephell.readthedocs.io/en/latest/cmd-generate-editorconfig.html), [LICENSE](https://dephell.readthedocs.io/en/latest/cmd-generate-license.html), [AUTHORS](https://dephell.readthedocs.io/en/latest/cmd-generate-authors.html).

See [documentation](https://dephell.readthedocs.io/) for more details.

## Installation

Simplest way:

```bash
python3 -m pip install --user dephell[full]
```

See [installation documentation](https://dephell.readthedocs.io/en/latest/installation.html) for better ways.
