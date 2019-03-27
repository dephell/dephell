# Lock poetry dependencies

Let's lock [poetry](https://github.com/sdispater/poetry) dependencies for dephell. First of all, get dephell source code:

```bash
git clone https://github.com/dephell/dephell.git
cd dephell
```

## With CLI arguments

```bash
$ dephell deps convert --from=pyproject.toml --to=poetry.lock
```

## With config

Add this in your `pyproject.toml`:

```toml
[tool.dephell.main]
from = {format = "poetry", path = "pyproject.toml"}
to = {format = "poetrylock", path = "poetry.lock"}
```

And then run:

```bash
$ dephell deps convert --config=pyproject.toml --env=main
```

Dephell by default uses `pyproject.toml` config and `main` section, so you can run it much simpler:

```bash
$ dephell deps convert
```

## More info

1. [How dephell works with config and parameters](config)
1. [`dephell convert` command](cmd-deps-convert)
