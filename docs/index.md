# DepHell

**DepHell** -- dependency management for Python.

+ Manage dependencies: convert between formats, install, lock, resolve conflicts.
+ Manage virtual environments: create, remove, run shell, run commands inside.
+ Install CLI tools into isolated environments.
+ Build packages (to upload on PyPI).
+ Discover licenses of all project dependencies.
+ Generate .editorconfig, LICENSE, AUTHORS.

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
    :caption: Project dependencies

    cmd-deps-add
    cmd-deps-audit
    cmd-deps-convert
    cmd-deps-install
    cmd-deps-licenses
    cmd-deps-outdated
    cmd-deps-tree

.. toctree::
    :maxdepth: 1
    :caption: Files generation

    cmd-generate-authors
    cmd-generate-config
    cmd-generate-editorconfig
    cmd-generate-license

.. toctree::
    :maxdepth: 1
    :caption: Inspect

    cmd-inspect-config
    cmd-inspect-self
    cmd-inspect-venv

.. toctree::
    :maxdepth: 1
    :caption: Isolation

    cmd-jail-install
    cmd-jail-list
    cmd-jail-remove

.. toctree::
    :maxdepth: 1
    :caption: Single package actions

    cmd-package-downloads
    cmd-package-install
    cmd-package-list
    cmd-package-search
    cmd-package-show

.. toctree::
    :maxdepth: 1
    :caption: Project

    cmd-project-bump

.. toctree::
    :maxdepth: 1
    :caption: Virtual environment

    cmd-venv-create
    cmd-venv-destroy
    cmd-venv-run
    cmd-venv-shell

.. toctree::
    :maxdepth: 1
    :caption: Other commands

    cmd-autocomplete
    cmd-project-build

.. toctree::
    :maxdepth: 1
    :caption: Recipes

    use-poetry-lock
    use-licenses
```
