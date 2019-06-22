# Pre-commit hook for git

[Pre-commit](https://pre-commit.com/) allows you to do some action before every commit. In these examples, you can generate `requirements.txt` and `setup.py` from `poetry`.

## Without DepHell config

Add next lines in [.pre-commit-config.yaml](https://github.com/mverteuil/precommit-dephell):

```yaml
- repo: https://github.com/mverteuil/precommit-dephell
  rev: master
  hooks:
    - id: pyproject-toml-to-setup-py
    - id: pyproject-toml-to-requirements-txt
```

## With DepHell config

If you have [dephell config](config) you can make the same things quite easier.

Add next lines in [.pre-commit-config.yaml](https://github.com/mverteuil/precommit-dephell):

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
