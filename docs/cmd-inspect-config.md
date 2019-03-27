# dephell inspect config

Shows current dephell config options. You can combine it with different arguments to inspect dephell behavior.

## Show all config

```bash
$ dephell inspect config
{
  "bin": "/home/gram/.local/bin",
  "bitbucket": "https://api.bitbucket.org/2.0",
  "cache": {
    "path": "/home/gram/.local/share/dephell/cache",
    "ttl": 3600
  },
  "envs": [
    "main"
  ],
  ...
  "warehouse": "https://pypi.org/pypi/"
}
```

## Filter output

Show one section:

```bash
$ dephell inspect config from
{
  "format": "poetry",
  "path": "pyproject.toml"
}

```

Show one value:

```bash
$ dephell inspect config from-format
poetry

$ dephell inspect config warehouse
https://pypi.org/pypi/
```

## Combine it with arguments

```bash
$ dephell inspect config --from-path=lol from
{
  "format": "poetry",
  "path": "lol"
}

$ dephell inspect config --from=setup.py from
{
  "format": "setuppy",
  "path": "setup.py"
}
```
