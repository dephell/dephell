# CHANGELOG

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
