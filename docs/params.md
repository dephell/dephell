# Parameters list

Parameters represented as CLI arguments. To make config file parameter name from CLI name just strip `--` from the begining and split by `-`.

For example, `--cache-path=.cache --` and `--project=./dephell` can be written in the next way:

```toml
[tool.dephell.main]
cache = {path = ".cache"}
project = "./dephell"
```

To make sure which of these options accepted by some command use `dephell COMMAND --help`. For example, `dephell deps convert --help`.

## Select config file and environment.

+ `-c`, `--config` -- path to config file.
+ `-e`, `--env` -- environment in config.

Of course, you can use this options only in CLI. You can't specify path to config in the config :)

## Paths to dependencies

+ `--from` -- path or format for reading requirements. If it is format then dephell will scan current directory to find out file that can be parsed by this converter. If it is filename then dephell will automatically determine file format.
+ `--from-format` -- format for reading requirements. See [deps convert](cmd-deps-convert) command documentation for full list of accepted formats.
+ `--from-path` -- path to input file.
+ `--to` -- path or format for writing requirements.
+ `--to-format` -- output requirements file format.
+ `--to-path` -- path to output file.

Commands that accept these parameters:

+ Only `deps convert` accepts `from` and `to` at the same time.
+ `deps install` prefers `to` option if available. This is because when you specified in config file source dependencies in `from` and locked dependencies in `to` then, of course, you want to install dependencies from lock file. However, if `to` (and `to-format` and `to-file`) isn't specified in the config and CLI arguments then `from` will be used.
+ `deps licenses` uses dependencies from `from`, lock them and shows licenses specified on PyPI.
+ `jail install`, `venv create`, `venv run`, and `venv shell` commands use `from` to determine preferred python version for project.

## Resolver and API

+ `--strategy` -- Algorithm to select best release. Available values: `min` and `max`. By default is `max`, because almost all resolvers uses this strategy. Read blog post [Minimal Version Selection](https://research.swtch.com/vgo-mvs) for details about `min` strategy.
+ `--prereleases` -- Allow prereleases.
+ `--warehouse` -- warehouse API URL. This is default value and can be reloaded in the dependencies file.
+ `--bitbucket` -- bitbucket API URL. Dephell isn't use Bitbucket API yet, but option already available.

## Virtual environment

+ `--venv` -- path to venv directory for project. Replacements:
    + `{project}` will be replaced by the project name (name of path from `project` option, this is name of the current directory by default).
    + `{digest}` will be replaced by the short 4-letters digest of the project path to avoid conflicts for the projects with the same name in different locations.
    + `{env}` will be replaced by current environment (`main` by default).
+ `--python` -- python version for venv. This can be reloaded in the dependencies file.

## Output

+ `--format` -- output format.
+ `--level` -- minimal level for log messages. Available levels: `DEBUG`, `INFO`, `WARNING`, `ERROR` and `EXCEPTION`. `INFO` by default. `DEBUG` and `INFO` writes in the stdout, other levels in the stderr.
+ `--nocolors` -- do not color output.
+ `--silent` -- suppress any output except errors. Disables progress bar for resolver.
+ `--traceback` -- show traceback for exceptions.

Other:

+ `--cache-path` -- path to dephell cache.
+ `--cache-ttl` -- Time to live for releases list cache (in seconds). 1 hour by default.
+ `--project` -- path to the current project. Current directory by default.
+ `--bin` -- path to the dir for installing scripts.
+ `--envs` -- environments (`main`, `dev`) or extras to install.

## Default values

Default values a little bit varies for different systems. Please, use [inspect config](cmd-inspect-config) to view your actual config for current sysstem, project and environment.
