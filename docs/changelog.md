# CHANGELOG

Follow [@PythonDepHell](https://twitter.com/PythonDepHell) on Twitter to get updates about new features and releases.

## v.0.7.4

+ Custom warehouse and simple index support ([#53](https://github.com/dephell/dephell/issues/53), [#128](https://github.com/dephell/dephell/pull/128)).
+ Fixed bug with packages names that made them incompatible with `pkg_resources` ([#110](https://github.com/dephell/dephell/issues/110), [#117](https://github.com/dephell/dephell/pull/117)).
+ Now `project bump` doesn't make git tag by default. Use `--tag` to add tag or add `tag = true` into config ([#114](https://github.com/dephell/dephell/pull/114), [#106](https://github.com/dephell/dephell/issues/106)).
+ Support for output into stdout for [dephell deps convert](cmd-deps-convert) ([#140](https://github.com/dephell/dephell/pull/140), [#136](https://github.com/dephell/dephell/issues/136)).
+ Allow to install prereleases into jail ([#118](https://github.com/dephell/dephell/pull/118), [#113](https://github.com/dephell/dephell/issues/113))
+ Smarter detection of owner name for `generate license`. You can force the name with `--owner=Name` (or `owner = "Name"` in config) ([#108](https://github.com/dephell/dephell/pull/108), [#107](https://github.com/dephell/dephell/issues/107), [#104](https://github.com/dephell/dephell/pull/104), [#87](https://github.com/dephell/dephell/issues/87)).
+ Local filesystem path support for `--warehouse` parameter ([#145](https://github.com/dephell/dephell/pull/145)).
+ Improved documentation ([#162](https://github.com/dephell/dephell/pull/162)).
+ Improved pre-release support for [dephell project bump](cmd-project-bump) ([#144](https://github.com/dephell/dephell/pull/144), [#142](https://github.com/dephell/dephell/issues/142)).
+ Improved poetry support ([#159](https://github.com/dephell/dephell/pull/159), [#152](https://github.com/dephell/dephell/issues/152), [#154](https://github.com/dephell/dephell/issues/154)).
+ Lazy load for bash autocomplete ([#132](https://github.com/dephell/dephell/pull/132)).

## v.0.7.3

+ Added `imports` converter to get dependencies from package imports ([#97](https://github.com/dephell/dephell/pull/97)).
+ `sdist` includes tests if they not too big (`--sdist-ratio` option) ([#99](https://github.com/dephell/dephell/pull/99), [#95](https://github.com/dephell/dephell/issues/95)).
+ You can specify path to `.env` file ([#69](https://github.com/dephell/dephell/issues/69), [#100](https://github.com/dephell/dephell/pull/100)).
+ `dephell package list` doesn't fail if some packages missed on PyPI ([#85](https://github.com/dephell/dephell/issues/85), [#102](https://github.com/dephell/dephell/pull/102)).

## v.0.7.2

+ [flit](https://flit.readthedocs.io/en/latest/pyproject_toml.html) support.
+ Missed meta information (like project version when you read from `requirements.txt`) will be automatically parsed from magic variables (like `__version__`) in the project source code.
+ Fix `plugins` parsing in poetry and `extras` parsing for `egg-info` and `sdist` ([#86](https://github.com/dephell/dephell/issues/86), [#89](https://github.com/dephell/dephell/pull/89)).
+ Fix `sdist` structure ([#94](https://github.com/dephell/dephell/pull/94), [#93](https://github.com/dephell/dephell/issues/93)).

## v.0.7.1

+ [`dependency_links`](https://setuptools.readthedocs.io/en/latest/setuptools.html#dependencies-that-aren-t-in-pypi) support for `setup.py`, `sdist` and `wheel` ([#79](https://github.com/dephell/dephell/pull/79), [#63](https://github.com/dephell/dephell/issues/63)).
+ Python 3.8 support ([#78](https://github.com/dephell/dephell/pull/78)).
+ Fix autocomplete for Mac OS X ([#65](https://github.com/dephell/dephell/pull/65), [#62](https://github.com/dephell/dephell/pull/62)).
+ Preserve dots in packages names ([#71](https://github.com/dephell/dephell/issues/71), [#80](https://github.com/dephell/dephell/pull/80), [pypa/pip#3666](https://github.com/pypa/pip/issues/3666)).
+ Make autocomplete for zsh really cool: added support for paths and choices ([#81](https://github.com/dephell/dephell/pull/81)).

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
