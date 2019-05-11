

.. image:: ./assets/logo.png
   :target: ./assets/logo.png
   :alt: DepHell

=============================================================================

Dependency resolution for Python.

Installation
------------

.. code-block:: bash

   sudo pip3 install dephell

CLI usage
---------

With arguments:

.. code-block:: bash

   python3 -m dephell convert \
       --from-format=pip --from-path=requirements.in \
       --to-format=piplock --to-path=requirements.txt

With config:

.. code-block:: bash

   python3 -m dephell convert --config=pyproject.toml --env=main

Mix config and arguments:

.. code-block:: bash

   python3 -m dephell convert --config=pyproject.toml \
       --to-format=piplock --to-path=requirements.txt

Available formats:


#. ``pip`` -- `pip's requirements file <https://pip.pypa.io/en/stable/user_guide/#id1>`_.
#. ``piplock`` -- `locked <https://pip.pypa.io/en/stable/reference/pip_freeze/>`_ pip's requirements file.
#. ``pipfile`` -- not locked `Pipfile <https://github.com/pypa/pipfile#pipfile>`_
#. ``pipfilelock`` -- locked `Pipfile <https://github.com/pypa/pipfile#pipfilelock>`_

Python lib usage
----------------

.. code-block:: python

   from dephell import PIPConverter, Requirement

   loader = PIPConverter(lock=False)
   resolver = loader.load_resolver(path='requirements.in')

   resolver.resolve()
   reqs = Requirement.from_graph(resolver.graph, lock=True)

   dumper = PIPConverter(lock=True)
   dumper.dump(reqs=reqs, path='requirements.txt')

TODO
----


#. poetry
#. poetry lock
#. Python version
#. Zero release (compatible with any constraints)
#. url defined release
#. git based dependency
