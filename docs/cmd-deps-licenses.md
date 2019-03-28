# dephell deps licenses

This command shows license for all your project's dependencies (from `from` section of current environment) in JSON format. Dephell detects the same license described in the different ways, like "MIT" and "MIT License", and combine these dependencies together. Dephell shows licenses **for all project's dependencies** including dependencies of dependencies.

```bash
$ dephell deps licenses

INFO resolved
{
  "Apache-2.0": [
    "aiofiles",
    "aiohttp",
    ...
  ],
  ...
  "Python Software Foundation License": [
    "backports-weakref",
    "editorconfig",
    "typing",
    "typing-extensions"
  ],
}
```

If you want to process this JSON to other tool disable dephell's helping output with `--level` and `--silent` arguments:

```bash
$ dephell deps licenses --level=WARNING --silent | jq --compact-output '."Apache-2.0"'
["aiofiles","aiohttp",...]
```

This example uses [jq](https://stedolan.github.io/jq/) to filter only one license from output. However, for simple filtering by license name you can just pass this name as positional argument in the command:

```bash
$ dephell deps licenses Apache-2.0

INFO resolved
[
  "aiofiles",
  "aiohttp",
  ...
]
```

## More info

1. [How dephell works with config and parameters](config)
1. [Full list of config parameters](params)
1. [Example of this command usage](use-licenses)
