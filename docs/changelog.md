# CHANGELOG

## v.0.7.1 (WIP)

+ [`dependency_links`](https://setuptools.readthedocs.io/en/latest/setuptools.html#dependencies-that-aren-t-in-pypi) support for `setup.py`.
+ Python 3.8 support ([#78](https://github.com/dephell/dephell/pull/78)).
+ Fix autocomplete for Mac OS X ([#65](https://github.com/dephell/dephell/pull/65), [#62](https://github.com/dephell/dephell/pull/62)).

## v.0.7.0

+ Filter dependencies by envs ([#56](https://github.com/dephell/dephell/issues/56), [#58](https://github.com/dephell/dephell/pull/58)).
+ Change API: now all import must be from the second level. For example, `from dephell.models import Dependency` instead of `from dephell import Dependency` or `from dephell.models.dependency import Dependency`.
+ Support for `allow-prereleases`, `python` and `platform` options in poetry ([#59](https://github.com/dephell/dephell/pull/59)).
+ [Serial versioning](https://packaging.python.org/guides/distributing-packages-using-setuptools/#serial-versioning) support ([#60](https://github.com/dephell/dephell/pull/60)).

## v.0.6.0

+ [Conda](https://github.com/conda/conda/) support ([#48](https://github.com/dephell/dephell/pull/48)).
    + [Anaconda Cloud](https://docs.anaconda.com/anaconda-cloud/).
    + Recipes from Github for [conda-forge](https://github.com/conda-forge/) and [bioconda](https://github.com/bioconda/bioconda-recipes/).
    + Support in `project show`, `project search` and `project releases`.
    + Converter for [environment.yml](https://docs.conda.io/projects/conda/en/latest/user-guide/tasks/manage-environments.html#sharing-an-environment).
+ Do not write hashes in `piplock` when some dependencies is local ([#41](https://github.com/dephell/dephell/issues/41), [#47](https://github.com/dephell/dephell/pull/47)).
+ Do not mess up setup.py on `project bump` ([#46](https://github.com/dephell/dephell/pull/46)).

## v.0.5.8

+ Fix some typos ([#43](https://github.com/dephell/dephell/issues/43), [#40](https://github.com/dephell/dephell/pull/40)).
+ Fix autocomplete when data direcotry wasn't created ([#42](https://github.com/dephell/dephell/issues/42)).
