# **vendor**: vendorize dependencies

[Vendorization](http://bitprophet.org/blog/2012/06/07/on-vendorizing/) is a placing external dependencies inside a folder in the project itself. It's a bad practice, but sometimes really useful and helpful. It allows you to pack dependencies inside your project to avoid conflicts with other packages, patch libraries, ship packages that aren't released on PyPI, make consistent environments etc. Use it only for internal projects and CLI tools. Never use it for libraries that used in other projects.

Some tools with vendorized dependencies: setuptools, pip, pipenv, pkg_resources.

DepHell can help you to [download and unpack](cmd-vendor-download) dependencies and [patch all imports](cmd-vendor-import).

```eval_rst
.. toctree::
    :maxdepth: 1

    cmd-vendor-download
    cmd-vendor-import
```
