

.. image:: ./assets/logo.png
   :target: ./assets/logo.png
   :alt: DepHell



.. image:: https://img.shields.io/pypi/v/dephell.svg
   :target: https://pypi.python.org/pypi/dephell/
   :alt: pypi


.. image:: https://img.shields.io/pypi/l/dephell.svg
   :target: https://github.com/dephell/dephell/blob/master/LICENSE
   :alt: MIT License


.. image:: https://travis-ci.org/dephell/dephell.svg?branch=master
   :target: https://travis-ci.org/dephell/dephell
   :alt: Travis CI


.. image:: ./assets/badge.svg
   :target: ./docs/badge.md
   :alt: Powered by DepHell


**DepHell** -- project management for Python.

Why it is better than all other tools:


#. **Format agnostic**. You can use DepHell with your favorite format: setup.py, requirements.txt, Pipfile, poetry. DepHell supports them all and much more.
#. **Use your favorite tool on any project**. Want to install a poetry based project, but don't like poetry? Just tell DepHell to convert the project's meta information into a setup.py and install it with pip. Or work directly work with the project from DepHell, because DepHell can do everything that you usually want to do with packages.
#. **DepHell doesn't try to replace your favorite tools**. If you use poetry, you have to use poetry's file formats and commands. However, DepHell can be combined with any other tool or can even combine all these tools together by converting formats. You can use DepHell, poetry, and pip all at the same time.
#. **Easily extendable**. DepHell has strong modularity and can be easily extended with new formats and commands.
#. **Developer friendly**. We aren't going to place all of our modules into `\ ``_internal`` <https://github.com/pypa/pip/tree/master/src/pip/_internal>`_. Also, DepHell has a `large ecosystem <https://github.com/dephell>`_ with separated libraries so you can use only the parts of DepHell that you need.
#. **All-in-one-solution**. DepHell can manage dependencies, virtual environments, tests, CLI tools, packages, generate configs, show licenses for dependencies, assist with security audits, get download statistics from PyPI, search packages and much more.
#. **Smart dependency resolution**. Sometimes pip and pipenv fail to lock your dependencies. Try to execute ``pipenv install oslo.utils==1.4.0``. Pipenv can't handle it, but DepHell can: ``dephell deps add --from=Pipfile oslo.utils==1.4.0`` to add new dependency and ``dephell deps convert --from=Pipfile --to=Pipfile.lock`` to lock it.
#. **Asyncio based**. DepHell doesn't support Python 2.7, and that allows us to use modern features to make network and filesystem requests as fast as possible.
#. **Multiple environments**. You can have as many environments for project as you want. Separate sphinx dependencies from your main and dev environment. Other tools like pipenv and poetry don't support this.

Features:


* Manage dependencies: `convert between formats <https://dephell.readthedocs.io/en/latest/cmd-deps-convert.html>`_\ , `instаll <https://dephell.readthedocs.io/en/latest/cmd-deps-install.html>`_\ , lock, `add new <https://dephell.readthedocs.io/en/latest/cmd-deps-add.html>`_\ , resolve conflicts.
* Manage virtual environments: `create <https://dephell.readthedocs.io/en/latest/cmd-venv-create.html>`_\ , `remove <https://dephell.readthedocs.io/en/latest/cmd-venv-destroy.html>`_\ , `inspect <https://dephell.readthedocs.io/en/latest/cmd-inspect-venv.html>`_\ , `run shell <https://dephell.readthedocs.io/en/latest/cmd-venv-shell.html>`_\ , `run commands inside <https://dephell.readthedocs.io/en/latest/cmd-venv-run.html>`_.
* `Install CLI tools <https://dephell.readthedocs.io/en/latest/cmd-jail-install.html>`_ into isolated environments.
* Manage packages: `install <https://dephell.readthedocs.io/en/latest/cmd-package-install.html>`_\ , `list <https://dephell.readthedocs.io/en/latest/cmd-package-list.html>`_\ , `search <https://dephell.readthedocs.io/en/latest/cmd-package-search.html>`_ on PyPI.
* `Build <https://dephell.readthedocs.io/en/latest/cmd-project-build.html>`_ packages (to upload on PyPI), `test <https://dephell.readthedocs.io/en/latest/cmd-project-test.html>`_\ , `bump project version <https://dephell.readthedocs.io/en/latest/cmd-project-bump.html>`_.
* `Discover licenses <https://dephell.readthedocs.io/en/latest/cmd-deps-licenses.html>`_ of all project dependencies, show `outdated <https://dephell.readthedocs.io/en/latest/cmd-deps-outdated.html>`_ packages, `find security issues <https://dephell.readthedocs.io/en/latest/cmd-deps-audit.html>`_.
* Generate `.editorconfig <https://dephell.readthedocs.io/en/latest/cmd-generate-editorconfig.html>`_\ , `LICENSE <https://dephell.readthedocs.io/en/latest/cmd-generate-license.html>`_\ , `AUTHORS <https://dephell.readthedocs.io/en/latest/cmd-generate-authors.html>`_\ , `.travis.yml <https://dephell.readthedocs.io/en/latest/cmd-generate-travis.html>`_.

See `documentation <https://dephell.readthedocs.io/>`_ for more details.

Follow `@PythonDepHell <https://twitter.com/PythonDepHell>`_ on Twitter to get updates about new features and releases.

Installation
------------

The simplest way:

.. code-block:: bash

   python3 -m pip install --user dephell[full]

See `installation documentation <https://dephell.readthedocs.io/en/latest/installation.html>`_ for better ways.

Supported formats
-----------------


#. Archives:

   #. `*.egg-info <https://setuptools.readthedocs.io/en/latest/formats.html>`_ (\ ``egginfo``\ )
   #. `*.tar.gz <https://packaging.python.org/glossary/#term-distribution-package>`_ (\ ``sdist``\ )
   #. `*.whl <https://pythonwheels.com>`_ (\ ``wheel``\ )

#. `pip <https://pip.pypa.io/en/stable/>`_\ :

   #. `requirements.txt <https://pip.pypa.io/en/stable/user_guide/#requirements-files>`_ (\ ``pip``\ )
   #. `requirements.lock <https://nvie.com/posts/pin-your-packages/>`_ (\ ``piplock``\ )

#. `pipenv <https://pipenv.readthedocs.io/en/latest/>`_\ :

   #. `Pipfile <https://github.com/pypa/pipfile>`_ (\ ``pipfile``\ )
   #. `Pipfile.lock <https://stackoverflow.com/a/49867443/8704691>`_ (\ ``pipfilelock``\ )

#. `pоetry <https://github.com/sdispater/poetry>`_\ :

   #. `pyproject.toml <https://poetry.eustace.io/docs/pyproject/>`_ (\ ``poetry``\ )
   #. `poetry.lock <https://poetry.eustace.io/docs/basic-usage/#installing-without-poetrylock>`_ (\ ``poetrylock``\ )

#. Environment:

   #. Imports in the package (\ ``imports``\ ).
   #. Installed packages (\ ``installed``\ ).

#. Other:

   #. `setup.py <https://docs.python.org/3/distutils/setupscript.html>`_ (\ ``setuppy``\ )
   #. `flit <https://flit.readthedocs.io/en/latest/pyproject_toml.html>`_ (\ ``flit``\ )
   #. `conda <https://conda.io/en/latest/>`_\ 's `environment.yml <https://docs.conda.io/projects/conda/en/latest/user-guide/tasks/manage-environments.html#creating-an-environment-file-manually>`_ (\ ``conda``\ )
   #. `pyproject.toml build-system requires <https://www.python.org/dev/peps/pep-0518/#build-system-table>`_ (\ ``pyproject``\ )

Usage
-----

First of all, install DepHell and activate autocomplete:

.. code-block:: bash

   python3 -m pip install --user dephell[full]
   dephell autocomplete

Let's get `sampleproject <https://github.com/pypa/sampleproject>`_ and make it better.

.. code-block:: bash

   git clone https://github.com/pypa/sampleproject.git
   cd sampleproject

This project uses `setup.py <https://docs.python.org/3/distutils/setupscript.html>`_ for dependencies and metainfo. However, this format is over-complicated for most projects. Let's convert it into `poetry <https://poetry.eustace.io/docs/pyproject/>`_\ :

.. code-block:: bash

   dephell deps convert --from=setup.py --to=pyproject.toml

It will make next ``pyproject.toml``\ :

.. code-block::

   [tool.poetry]
   name = "sampleproject"
   version = "1.2.0"
   description = "A sample Python project"
   authors = ["The Python Packaging Authority <pypa-dev@googlegroups.com>"]
   readme = "README.md"

   [tool.poetry.scripts]
   sample = "sample:main"

   [tool.poetry.dependencies]
   python = "!=3.0.*,!=3.1.*,!=3.2.*,!=3.3.*,<4,>=2.7"
   coverage = {optional = true}
   peppercorn = "*"

   [tool.poetry.dev-dependencies]
   check-manifest = "*"

   [tool.poetry.extras]
   test = ["coverage"]

Now, let's generate some useful files:

.. code-block:: bash

   dephell generate authors

   dephell generate license MIT

   # https://editorconfig.org/
   dephell generate editorconfig

Our users probably have not installed poetry, but they are likely to have pip and can install files from setup.py. Let's make it easier to generate ``setup.py`` from our ``pyproject.toml``. Also, it points to DepHell as your default dependencies file. Add the following lines in the ``pyproject.toml``\ :

.. code-block::

   [tool.dephell.main]
   from = {format = "poetry", path = "pyproject.toml"}
   to = {format = "setuppy", path = "setup.py"}

You can see a full, real-world example of a config in `DepHell's own pyproject.toml <./pyproject.toml>`_.

Now we can call DepHell commands without explicitly specifying ``from`` and ``to``\ :

.. code-block:: bash

   dephell deps convert

It will make setup.py and README.rst from pyproject.toml and README.md.

Now let's test our code in a virtual environment:

.. code-block:: bash

   $ dephell venv run pytest
   WARNING venv does not exist, creating... (project=/home/gram/Documents/sampleproject, env=main, path=/home/gram/.local/share/dephell/venvs/sampleproject-Whg0/main)
   INFO venv created (path=/home/gram/.local/share/dephell/venvs/sampleproject-Whg0/main)
   WARNING executable does not found in venv, trying to install... (executable=pytest)
   INFO build dependencies graph...
   INFO installation...
   # ... pip output
   # ... pytest output

We can now activate the virtual environment for our project and run any commands inside:

.. code-block:: bash

   dephell venv shell

Ugh, we have tests, but don't have ``pytest`` in our dependencies file. Let's add it:

.. code-block:: bash

   dephell deps add --envs dev test -- pytest

Afer that our dev-dependencies looks like this:

.. code-block::

   [tool.poetry.dev-dependencies]
   check-manifest = "*"
   pytest = "*"

   [tool.poetry.extras]
   test = ["coverage", "pytest"]

Eventually we will have many more dependencies. Let's look at how many of them we have now:

.. code-block:: bash

   $ dephell deps tree
   - check-manifest [required: *, locked: 0.37, latest: 0.37]
   - coverage [required: *, locked: 4.5.3, latest: 4.5.3]
   - peppercorn [required: *, locked: 0.6, latest: 0.6]
   - pytest [required: *, locked: 4.4.0, latest: 4.4.0]
     - atomicwrites [required: >=1.0, locked: 1.3.0, latest: 1.3.0]
     - attrs [required: >=17.4.0, locked: 19.1.0, latest: 19.1.0]
     - colorama [required: *, locked: 0.4.1, latest: 0.4.1]
     - funcsigs [required: >=1.0, locked: 1.0.2, latest: 1.0.2]
     - more-itertools [required: <6.0.0,>=4.0.0, locked: 5.0.0, latest: 7.0.0]
       - six [required: <2.0.0,>=1.0.0, locked: 1.12.0, latest: 1.12.0]
     - more-itertools [required: >=4.0.0, locked: 7.0.0, latest: 7.0.0]
     - pathlib2 [required: >=2.2.0, locked: 2.3.3, latest: 2.3.3]
       - scandir [required: *, locked: 1.10.0, latest: 1.10.0]
       - six [required: *, locked: 1.12.0, latest: 1.12.0]
     - pluggy [required: >=0.9, locked: 0.9.0, latest: 0.9.0]
     - py [required: >=1.5.0, locked: 1.8.0, latest: 1.8.0]
     - setuptools [required: *, locked: 41.0.0, latest: 41.0.0]
     - six [required: >=1.10.0, locked: 1.12.0, latest: 1.12.0]

Hm...Is it as many as it seems? Let's look at their size.

.. code-block:: bash

   $ dephell inspect venv --filter=lib_size
   11.96Mb

Ugh...Ok, it's Python. Are they actual?

.. code-block:: bash

   $ dephell deps outdated
   [
     {
       "description": "More routines for operating on iterables, beyond itertools",
       "installed": [
         "5.0.0"
       ],
       "latest": "7.0.0",
       "name": "more-itertools",
       "updated": "2019-03-28"
     },
   ]

``Pytest`` requires old version of ``more-itertools``. That happens.

If our tests and dependencies are OK, it's time to deploy. First of all, increment the project version:

.. code-block:: bash

   $ dephell project bump minor
   INFO generated new version (old=1.2.0, new=1.3.0)

And then build packages:

.. code-block:: bash

   $ dephell project build
   INFO dumping... (format=setuppy)
   INFO dumping... (format=egginfo)
   INFO dumping... (format=sdist)
   INFO dumping... (format=wheel)
   INFO builded

Now, we can upload these packages to `PyPI <https://pypi.org/>`_ with `twine <https://github.com/pypa/twine/>`_.

These are some of the most useful commands. See `documentation <https://dephell.readthedocs.io/>`_ for more details.

Compatibility
-------------

DepHell is tested on Linux and Mac OS X with Python 3.5, 3.6, 3.7. And one of the coolest things is that DepHell is run by DepHell on Travis CI.

How can I help
--------------


#. Star project on Github. Developers believe in the stars.
#. Tell your fellows that `Gram <http://github.com/orsinium>`_ has a made `cool thing <https://github.com/dephell/dephell>`_ for you.
#. `Open an issue <https://github.com/dephell/dephell/issues/new>`_ if you have thoughts on how to make DepHell better.
#. Things that you can contribute in any project in `DepHell ecosystem <https://github.com/dephell>`_\ :

   #. Fix grammar and typos.
   #. Document new things.
   #. Tests, we always need more tests.
   #. Make READMEs more nice and friendly.
   #. View issues with the `help wanted <https://github.com/dephell/dephell/issues?q=is%3Aissue+is%3Aopen+label%3A%22help+wanted%22>`_ label to find things that you can fix.
   #. Anything what you want. If it is a new feature, please open an issue before writing code.

Thank you :heart:
