# Pre-commit hook for git

## Without DepHell config

Configure hooks in [.pre-commit-hooks.yaml](https://github.com/mverteuil/precommit-dephell/blob/master/.pre-commit-hooks.yaml):

```yaml
- id: pyproject-toml-to-setup-py
  name: Convert pyproject.toml to setup.py
  description: Generate setup.py from pyproject.toml for backwards compatibility using 'dephell'.
  language: system
  entry: dephell deps convert --from=pyproject.toml --to=setup.py
  files: "^pyproject.toml$"
  pass_filenames: false

- id: pyproject-toml-to-requirements-txt
  name: Convert pyproject.toml to requirements.txt
  description: Generate requirements.txt pyproject.toml for backwards compatibility using 'dephell'.
  language: system
  entry: dephell deps convert --from=pyproject.toml --to=requirements.txt
  files: "^pyproject.toml$"
  pass_filenames: false
```

Enable hooks in [.pre-commit-config.yaml](https://github.com/mverteuil/precommit-dephell):

```yaml
- repo: https://github.com/mverteuil/precommit-dephell
  rev: master
  hooks:
    - id: pyproject-toml-to-setup-py
    - id: pyproject-toml-to-requirements-txt
```

## With DepHell config

If you have [dephell config](config) you can make the same things quite easier.

Configure hook in [.pre-commit-hooks.yaml](https://github.com/mverteuil/precommit-dephell/blob/master/.pre-commit-hooks.yaml):

```yaml
- id: dephell
  name: Run dephell with defaults
  description: Generate default output based on configuration in pyproject.toml. See https://dephell.readthedocs.io for configuration options.
  language: system
  entry: dephell deps convert
  pass_filenames: false
```

Enable hook in [.pre-commit-config.yaml](https://github.com/mverteuil/precommit-dephell):

```yaml
- repo: https://github.com/mverteuil/precommit-dephell
  rev: master
  hooks:
    - id: dephell
```

## See also

1. [Source repository](https://github.com/mverteuil/precommit-dephell).
1. [DepHell config](config).
1. [Hooks in Git](https://githooks.com/).
