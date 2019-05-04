# Packaging issues

My favorite issues collection.

## Pip

1. Pip doesn't support Pipfile ([pipfile#80](https://github.com/pypa/pipfile/issues/80)).
1. Pip doesn't have dependency resolution ([pip#988](https://github.com/pypa/pip/issues/988))

## Pipenv

1. Pipenv doesn't support more than 2 environments for project ([pipfile#99](https://github.com/pypa/pipfile/issues/99)).
1. Pipenv doesn't support "allow pre-releases" option for single dependency ([pipenv#1760](https://github.com/pypa/pipenv/issues/1760)).
1. Pipenv doesn't support python version range ([pipfile#87](https://github.com/pypa/pipfile/issues/87)).

## Poetry

1. Poetry supports only `platform` and `python` specification. This is not documented ([poetry#738](https://github.com/sdispater/poetry/issues/738)). This doesn't allow you to specify other markers like python implementation ([poetry#21](https://github.com/sdispater/poetry/issues/21)).
1. Poetry doesn't allow you to specify editable dependencies in the config ([poetry#34](https://github.com/sdispater/poetry/issues/34)).

## PyPI

1. PyPI API doesn't provide dependecies list for some packages ([packaging-problems#54](https://github.com/pypa/packaging-problems/issues/54) and [warehouse#789](https://github.com/pypa/warehouse/issues/789)).
