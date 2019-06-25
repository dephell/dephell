# dephell deps add

Add new dependencies into project.

Algorithm:

1. Get dependencies from `from` file.
1. Add new dependencies.
1. Check that these new dependencies has no conflicts with existing.
1. Write dependencies back into `from` file.

You can specify `--envs` to add dependencies into.

## Basic usage

Simple usage:

```bash
dephell deps add --from=poetry flake8
```

Best practice is specify your dependencies file in `pyproject.toml` DepHell config:

```bash
[tool.dephell.main]
from = {format = "poetry", path = "pyproject.toml"}
```

And after that DepHell will automatically detect your dependencies file:

```bash
dephell deps add flake8
```

See [configuration documentation](config) for more details.

## Specify dependencies environments

Environments for dependencies is the name of dependencies section (`main` and `dev` for `poetry` and `pipfile`) or name of [extras](https://setuptools.readthedocs.io/en/latest/setuptools.html#declaring-extras-optional-features-with-their-own-dependencies). DepHell uses `main` by default, but you can specify another one:

```bash
dephell deps add --envs dev tests -- flake8==3.1.0 pytest
```

This will produce dependencies next lines in your poetry config:

```toml
[tool.poetry.dev-dependencies]
pytest = "*"
flake8 = "==3.1.0"

[tool.poetry.extras]
tests = ["flake8", "pytest"]
```

## See also

1. [How to configure DepHell](config).
1. [How to filter commands JSON output](filters).
1. [dephell deps convert](cmd-deps-convert) for details about locking dependencies and supported file formats.
1. [dephell deps install](cmd-deps-install) to install new dependencies into virtual environment.
1. [dephell package install](cmd-package-list) to install single package without adding it into requirements.
