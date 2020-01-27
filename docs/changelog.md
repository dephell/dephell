# CHANGELOG

Follow [@PythonDepHell](https://twitter.com/PythonDepHell) on Twitter to get updates about new features and releases.

## v.0.8.1 (2020-01-27)

New commands:

+ [dephell package changelog](https://dephell.readthedocs.io/cmd-package-changelog.html) ([#361](https://github.com/dephell/dephell/pull/361)).

Improvements:

+ Experimental Windows support. Test it and contribute! ([#343](https://github.com/dephell/dephell/issues/343)). Special thanks to [@espdev](https://github.com/espdev) who has done almost all the migration.
+ Lazy imports. About 10 dependencies were converted into optional and will be installed by-demand. Installation with `curl -L dephell.org/install | python3` isn't affected. ([#349](https://github.com/dephell/dephell/pull/349))
+ Support new pip ([362](https://github.com/dephell/dephell/pull/362)) and lock older pip because a new one is broken ([#363](https://github.com/dephell/dephell/pull/363))
+ Rewritten installer ([#365](https://github.com/dephell/dephell/pull/365), [#355](https://github.com/dephell/dephell/pull/355))
+ [a little bit more](https://github.com/dephell/dephell/milestone/4?closed=1).

## v.0.8.0 (2019-12-19)

New commands:

+ [dephell package bug](https://dephell.readthedocs.io/cmd-package-bug.html) ([#318](https://github.com/dephell/dephell/pull/318)).
+ [dephell jail show](https://dephell.readthedocs.io/cmd-jail-show.html) ([#318](https://github.com/dephell/dephell/pull/319)).
+ [dephell inspect versioning](https://dephell.readthedocs.io/cmd-inspect-versioning.html) ([#318](https://github.com/dephell/dephell/pull/320)).

Improvements:

+ Meet [dephell_argparse](https://github.com/dephell/dephell_argparse) ([#317](https://github.com/dephell/dephell/pull/317)).
+ Meet [DepHell-powered projects](https://dephell.readthedocs.io/use-projects.html) list ([#339](https://github.com/dephell/dephell/pull/339))
+ Rename `dephell autocomplete` into `dephell self autocomplete`, and `dephell auth` into `dephell self auth` ([#321](https://github.com/dephell/dephell/pull/321)).
+ Support `allow-prereleases` key from Poetry 1.0.0 ([#323](https://github.com/dephell/dephell/pull/323))
+ From now DepHell will not be tested on Python 3.5 installation because nobody installs DepHell on Python 3.5 ([#334](https://github.com/dephell/dephell/pull/334)).
+ [a little bit more](https://github.com/dephell/dephell/milestone/3?closed=1).

## v.0.7.9 (2019-11-19)

New commands:

+ [dephell self uncache](cmd-self-uncache) ([#312](https://github.com/dephell/dephell/pull/312)).
+ [dephell self upgrade](cmd-self-upgrade) ([#311](https://github.com/dephell/dephell/pull/311)).
+ [dephell generate contributing](cmd-generate-contributing) ([#255](https://github.com/dephell/dephell/pull/255)).
+ [dephell inspect project](cmd-inspect-project) ([#296](https://github.com/dephell/dephell/pull/296)).
+ [dephell project validate](cmd-project-validate) ([#310](https://github.com/dephell/dephell/pull/310)).

Improvements:

+ Smart `setup.py` parsing. Meet [dephell_setuptools](https://github.com/dephell/dephell_setuptools) ([#308](https://github.com/dephell/dephell/pull/308)).
+ Stable `setup.py` generation ([#292](https://github.com/dephell/dephell/pull/292)).
+ Cleaner sdist ([#297](https://github.com/dephell/dephell/pull/297)).
+ [a little bit more](https://github.com/dephell/dephell/milestone/2?closed=1)

## v.0.7.8 (2019-10-22)

+ Fuzzy command name search ([#247](https://github.com/dephell/dephell/pull/247), [#122](https://github.com/dephell/dephell/issues/122)).
+ [Configure](config) DepHell with environment variables ([#248](https://github.com/dephell/dephell/pull/248)).
+ Colored JSON output ([#262](https://github.com/dephell/dephell/pull/262), [#260](https://github.com/dephell/dephell/pull/260), [#205](https://github.com/dephell/dephell/issues/205)).
+ Table output with `--table` ([#277](https://github.com/dephell/dephell/pull/277), [#267](https://github.com/dephell/dephell/pull/267), [#206](https://github.com/dephell/dephell/issues/206)).
+ New [attrs](https://www.attrs.org) ([#261](https://github.com/dephell/dephell/pull/261)).
+ ruamel.yaml instead of pyyaml ([#275](https://github.com/dephell/dephell/pull/275))
+ pip 19.3.1 support ([#276](https://github.com/dephell/dephell/pull/276)).
+ [a little bit more](https://github.com/dephell/dephell/milestone/1?closed=1)

## v.0.7.7 (2019-07-23)

+ Meet [dephell.org](https://dephell.org/) ([#244](https://github.com/dephell/dephell/pull/244)).
+ Lazy dependencies overwriting ([#232](https://github.com/dephell/dephell/pull/232), [#229](https://github.com/dephell/dephell/issues/229)).
+ Removed Snyk support ([#245](https://github.com/dephell/dephell/pull/245)).
+ Added custom User-Agent to all requests ([#242](https://github.com/dephell/dephell/pull/242), [#243](https://github.com/dephell/dephell/pull/243), [#231](https://github.com/dephell/dephell/issues/231))
+ Updated documentation interface ([#241](https://github.com/dephell/dephell/pull/241)).
+ `path` support for `pip`, `pipenv`, `poetry` ([#230](https://github.com/dephell/dephell/pull/230), [#227](https://github.com/dephell/dephell/issues/227)).

## v.0.7.6 (2019-07-17)

+ Docker support ([#220](https://github.com/dephell/dephell/pull/220), [#49](https://github.com/dephell/dephell/issues/49)).
+ Fixed dependencies for DepHell itself ([#218](https://github.com/dephell/dephell/pull/218), [#216](https://github.com/dephell/dephell/issues/216)).
+ Resolve paths to dependency files relatively to the project, and local dependencies relatively to the dependency file ([#217](https://github.com/dephell/dephell/pull/217), [#88](https://github.com/dephell/dephell/issues/88)).
+ Fixed repositories dumping for poetry ([#215](https://github.com/dephell/dephell/pull/215), [#177](https://github.com/dephell/dephell/issues/177)).
+ Simplified "usage" for commands' help ([#212](https://github.com/dephell/dephell/pull/212), [#120](https://github.com/dephell/dephell/issues/120)).
+ Install extras in [dephell project test](cmd-project-test) if needed ([#204](https://github.com/dephell/dephell/pull/204), [#195](https://github.com/dephell/dephell/issues/195)).

## v.0.7.5 (2019-07-07)

+ Vendorization ([dephell vendor download](cmd-vendor-download) and [dephell vendor import](cmd-vendor-import)) ([#194](https://github.com/dephell/dephell/pull/194), [#109](https://github.com/dephell/dephell/issues/109))
+ Now CLI for some commands accepts `--from` instead of `--to`, because it makes much more sense ([#194](https://github.com/dephell/dephell/pull/194), [#138](https://github.com/dephell/dephell/issues/138))
+ Always PEP-compatible name for names of wheel and sdist ([#203](https://github.com/dephell/dephell/pull/203), [#192](https://github.com/dephell/dephell/issues/192))
+ Now `--tag` option for [dephell project bump](cmd-project-bump) allows to specify tag prefix or template ([#199](https://github.com/dephell/dephell/pull/199), [#197](https://github.com/dephell/dephell/issues/197))
+ Meet [dephell_versioning](https://github.com/dephell/dephell_versioning), our new friend to handle packages versioning ([#191](https://github.com/dephell/dephell/pull/191), [#147](https://github.com/dephell/dephell/issues/147))
+ Shorter links in documentation ([#183](https://github.com/dephell/dephell/pull/183), [#182](https://github.com/dephell/dephell/issues/182))

## v.0.7.4 (2019-06-17)

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

## v.0.7.3 (2019-05-19)

+ Added `imports` converter to get dependencies from package imports ([#97](https://github.com/dephell/dephell/pull/97)).
+ `sdist` includes tests if they not too big (`--sdist-ratio` option) ([#99](https://github.com/dephell/dephell/pull/99), [#95](https://github.com/dephell/dephell/issues/95)).
+ You can specify path to `.env` file ([#69](https://github.com/dephell/dephell/issues/69), [#100](https://github.com/dephell/dephell/pull/100)).
+ `dephell package list` doesn't fail if some packages missed on PyPI ([#85](https://github.com/dephell/dephell/issues/85), [#102](https://github.com/dephell/dephell/pull/102)).

## v.0.7.2 (2019-05-19)

+ [flit](https://flit.readthedocs.io/en/latest/pyproject_toml.html) support.
+ Missed meta information (like project version when you read from `requirements.txt`) will be automatically parsed from magic variables (like `__version__`) in the project source code.
+ Fix `plugins` parsing in poetry and `extras` parsing for `egg-info` and `sdist` ([#86](https://github.com/dephell/dephell/issues/86), [#89](https://github.com/dephell/dephell/pull/89)).
+ Fix `sdist` structure ([#94](https://github.com/dephell/dephell/pull/94), [#93](https://github.com/dephell/dephell/issues/93)).

## v.0.7.1 (2019-05-12)

+ [`dependency_links`](https://setuptools.readthedocs.io/en/latest/setuptools.html#dependencies-that-aren-t-in-pypi) support for `setup.py`, `sdist` and `wheel` ([#79](https://github.com/dephell/dephell/pull/79), [#63](https://github.com/dephell/dephell/issues/63)).
+ Python 3.8 support ([#78](https://github.com/dephell/dephell/pull/78)).
+ Fix autocomplete for Mac OS X ([#65](https://github.com/dephell/dephell/pull/65), [#62](https://github.com/dephell/dephell/pull/62)).
+ Preserve dots in packages names ([#71](https://github.com/dephell/dephell/issues/71), [#80](https://github.com/dephell/dephell/pull/80), [pypa/pip#3666](https://github.com/pypa/pip/issues/3666)).
+ Make autocomplete for zsh really cool: added support for paths and choices ([#81](https://github.com/dephell/dephell/pull/81)).

## v.0.7.0 (2019-05-05)

+ Filter dependencies by envs ([#56](https://github.com/dephell/dephell/issues/56), [#58](https://github.com/dephell/dephell/pull/58)).
+ Change API: now all import must be from the second level. For example, `from dephell.models import Dependency` instead of `from dephell import Dependency` or `from dephell.models.dependency import Dependency`.
+ Support for `allow-prereleases`, `python` and `platform` options in poetry ([#59](https://github.com/dephell/dephell/pull/59)).
+ [Serial versioning](https://packaging.python.org/guides/distributing-packages-using-setuptools/#serial-versioning) support ([#60](https://github.com/dephell/dephell/pull/60)).

## v.0.6.0 (2019-04-30)

+ [Conda](https://github.com/conda/conda/) support ([#48](https://github.com/dephell/dephell/pull/48)).
    + [Anaconda Cloud](https://docs.anaconda.com/anaconda-cloud/).
    + Recipes from Github for [conda-forge](https://github.com/conda-forge/) and [bioconda](https://github.com/bioconda/bioconda-recipes/).
    + Support in `project show`, `project search` and `project releases`.
    + Converter for [environment.yml](https://docs.conda.io/projects/conda/en/latest/user-guide/tasks/manage-environments.html#sharing-an-environment).
+ Do not write hashes in `piplock` when some dependencies is local ([#41](https://github.com/dephell/dephell/issues/41), [#47](https://github.com/dephell/dephell/pull/47)).
+ Do not mess up setup.py on `project bump` ([#46](https://github.com/dephell/dephell/pull/46)).

## v.0.5.8 (2019-04-25)

+ Fix some typos ([#43](https://github.com/dephell/dephell/issues/43), [#40](https://github.com/dephell/dephell/pull/40)).
+ Fix autocomplete when data directory wasn't created ([#42](https://github.com/dephell/dephell/issues/42)).

## Before

+ The first public release: 2019-03-14.
+ The first proof-of-concept: 2018-09-03.
