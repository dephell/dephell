# DepHell

**DepHell** -- project management for Python.

+ Manage dependencies: [convert between formats](cmd-deps-convert), [install](cmd-deps-install), lock, [add new](cmd-deps-add), resolve conflicts.
+ Manage virtual environments: [create](cmd-venv-create), [remove](cmd-venv-destroy), [inspect](cmd-inspect-venv), [run shell](cmd-venv-shell), [run commands inside](cmd-venv-run).
+ [Install CLI tools](cmd-jail-install) into isolated environments.
+ Manage packages: [install](cmd-package-install), [list](cmd-package-list), [search](cmd-package-search) on PyPI.
+ [Build](cmd-project-build) packages (to upload on PyPI), [test](cmd-project-test), [bump project version](cmd-project-bump).
+ [Discover licenses](cmd-deps-licenses) of all project dependencies, show [outdated](cmd-deps-outdated) packages, [find security issues](cmd-deps-audit).
+ Generate [.editorconfig](cmd-generate-editorconfig), [LICENSE](cmd-generate-license), [AUTHORS](cmd-generate-authors), [.travis.yml](cmd-generate-travis).

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
    :maxdepth: 2
    :caption: Commands

    index-deps
    index-generate
    index-inspect
    index-jail
    index-package
    index-project
    index-venv
    index-other

.. toctree::
    :maxdepth: 1
    :caption: Dive deeper

    badge
    changelog
    hell

.. toctree::
    :maxdepth: 1
    :caption: Recipes and examples

    use-git-hook
    use-tree-git
    use-poetry-lock
    use-licenses
```
