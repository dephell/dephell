# DepHell

**DepHell** -- project management for Python.

+ Manage dependencies: [convert between formats](cmd-deps-convert), [install](cmd-deps-install), lock, [add new](cmd-deps-add), resolve conflicts.
+ Manage virtual environments: [create](cmd-venv-create), [remove](cmd-venv-destroy), [inspect](cmd-inspect-venv), [run shell](cmd-venv-shell), [run commands inside](cmd-venv-run).
+ [Install CLI tools](cmd-jail-install) into isolated environments.
+ Manage packages: [install](cmd-package-install), [list](cmd-package-list), [search](cmd-package-search) on PyPI.
+ [Build](cmd-project-build) packages (to upload on PyPI), [test](cmd-project-test), [bump project version](cmd-project-bump).
+ [Discover licenses](cmd-deps-licenses) of all project dependencies, show [outdated](cmd-deps-outdated) packages, [find security issues](cmd-deps-audit).
+ Generate [.editorconfig](cmd-generate-editorconfig), [LICENSE](cmd-generate-license), [AUTHORS](cmd-generate-authors), [.travis.yml](cmd-generate-travis).

## Quick start

1. [Install](installation) DepHell.
1. [Convert](cmd-deps-convert) dependencies from one format to another.
1. [Make config](config) for DepHell to simplify commands.

And that's it! Now you can use any tools with any Python project. Every other commands build around ability to read project dependencies and metadata and resolve conflicts. When you ready to boost your productivity, read how to manage your environment with DepHell:

1. [Create virtual environment](cmd-venv-create).
1. [Install](cmd-deps-install) or [synchronize](cmd-deps-sync) dependencies.
1. [Run](cmd-venv-run) commands inside or [activate virtual environment](cmd-venv-shell).

```eval_rst
.. toctree::
    :maxdepth: 1
    :caption: Main Info

    installation
    config
    params
    filters
    python-lookup

.. toctree::
    :maxdepth: 1
    :caption: Commands

    index-deps
    index-docker
    index-generate
    index-inspect
    index-jail
    index-package
    index-project
    index-self
    index-vendor
    index-venv

.. toctree::
    :maxdepth: 1
    :caption: Dive deeper

    index-use
    badge
    changelog
    hell
```
