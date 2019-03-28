# Show licenses for your dependencies

You can use [dephell deps licenses](cmd-deps-licenses) command to reveal licenses for all dependencies (and dependencies of dependencies) of your project. For example, let's get licenses for flake8 plugins of dephell. First of all, get dephell source code:

```bash
git clone https://github.com/dephell/dephell.git
cd dephell
```

## With CLI arguments

```bash
$ dephell deps licenses --from-format=pip --from-path=requirements-flake.txt

INFO resolved
{
  "BSD-2-Clause": [
    "enum34"
  ],
  ...
  "Unknown": [
    "flake8-logging-format"
  ]
}
```

## With config

Dephell contains this section in the `pyproject.toml`:

```toml
[tool.dephell.flake8]
from = {format = "pip", path = "requirements-flake.txt"}
```

So, you can write command above quite shorter:

```bash
$ dephell deps licenses --env=flake8
```

## More info

1. [How dephell works with config and parameters](config)
1. [`dephell deps licenses` command](cmd-deps-licenses)
