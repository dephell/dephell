# Private PyPI repository

## Add PyPI URL

By default, DepHell uses [pypi.org](https://pypi.org/) as warehouse repository:

```bash
$ dephell inspect config --filter="warehouse"
[
  "https://pypi.org/pypi/"
]
```

You can reload it with `--warehouse` [parameter](params):

```bash
$ dephell inspect config --warehouse example1.com example2.com --filter="warehouse"
[
  "example1.com",
  "example2.com"
]
```

You can specify it in the [DepHell config](config):

```toml
[tool.dephell.main]
warehouse = ["example1.com", "example2.com"]
```

DepHell supports path to local directory with releases archives:

```toml
[tool.dephell.main]
warehouse = ["./path/to/releases"]
```

If you explicitly specify `warehouse`, DepHell drops default value and don't use [pypi.org](https://pypi.org/) anymore. If you want to use it after your private repository, also add it in the list:

```bash
dephell inspect config --warehouse https://example1.com/simple https://pypi.org/ --filter="warehouse"
[
  "https://example1.com/simple",
  "https://pypi.org/"
]
```

You can remove any repositories at all to use only specified in dependencies file:

```bash
$ dephell inspect config --warehouse --filter="warehouse"
[]
```

# Authentication

Use [dephell auth](cmd-auth) to add credentials for host in global config:

```bash
$ dephell auth example.com gram "p@ssword"
INFO credentials added (hostname=example.com, username=gram)
```

You can list stored credentials with [dephell inspect auth](cmd-inspect-auth):

```bash
$ dephell inspect auth
[
  {
    "hostname": "example.com",
    "password": "p@ssword",
    "username": "gram"
  }
]
```

## Repositories from dependency file

Some dependency formats supports explicit repository specification. These repositories always have higher priority than specified in config.

`requirements.txt`:

```
-i https://example.com/
-i https://pypi.org/simple/
...
```
