# Parameters list

Parameters represented as CLI arguments. To make config file parameter name from CLI name just strip `--` from the begining and split by `-`.

For example, `--cache-path=.cache --` and `--project=./dephell` can be written in the next way:

```toml
[tool.dephell.main]
cache = {path = ".cache"}
project = "./dephell"
```

To make sure which of these options accepted by some command use `dephell COMMAND --help`. For example, `dephell deps convert --help`.

## Full list

Select config file and environment:

+ `-c`, `--config` -- path to config file.
+ `-e`, `--env` -- environment in config.

Paths to dependencies:

+ `--from` -- path or format for reading requirements.
+ `--from-format` -- format for reading requirements.
+ `--from-path` -- path to input file.
+ `--to` -- path or format for writing requirements.
+ `--to-format` -- output requirements file format.
+ `--to-path` -- path to output file.

Resolver and API:

+ `--strategy` -- Algorithm to select best release.
+ `--prereleases` -- Allow prereleases.
+ `--warehouse` -- warehouse API URL.
+ `--bitbucket` -- bitbucket API URL.

Virtual environment:

+ `--venv` -- path to venv directory for project.
+ `--python` -- python version for venv.

Output:

+ `--format` -- output format.
+ `--level` -- minimal level for log messages.
+ `--nocolors` -- do not color output.
+ `--silent` -- suppress any output except errors.
+ `--traceback` -- show traceback for exceptions.

Other:

+ `--cache-path` -- path to dephell cache.
+ `--cache-ttl` -- Time to live for releases list cache.
+ `--project` -- path to the current project.
+ `--bin` -- path to the dir for installing scripts.
+ `--envs` -- environments (main, dev) or extras to install.
