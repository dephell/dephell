# Filter JSON output

JSON output of any command can be filtered with `--filter` argument.

## Commands with JSON output

+ [dephell deps licenses](cmd-deps-licenses)
+ [dephell inspect config](cmd-inspect-config)
+ [dephell inspect venv](cmd-inspect-venv)
+ [dephell jail list](cmd-jail-list)
+ [dephell package list](cmd-package-list)
+ [dephell package search](cmd-package-search)
+ [dephell package show](cmd-package-show)

## Example

Let's filter output of [dephell package show](cmd-package-show):

```bash
$ dephell package show textdistance
{
  "authors": [
    "orsinium <master_fess@mail.ru>"
  ],
  "description": "Compute distance between the two texts.",
  "license": "MIT",
  "links": {
    "download": "https://github.com/orsinium/textdistance/tarball/master",
    "homepage": "https://github.com/orsinium/textdistance",
    "package": "https://pypi.org/project/textdistance/"
  },
  "name": "textdistance",
  "version": {
    "installed": null,
    "latest": "4.1.2"
  }
}
```

Get field:

```bash
$ dephell package show --filter=version textdistance
{
  "installed": null,
  "latest": "4.1.2"
}

$ dephell package show --filter=version.latest textdistance
4.1.2
```

Filter list items:

```bash
$ dephell package show --filter=authors click
[
  "Armin Ronacher <armin.ronacher@active-4.com>",
  "Pallets Team <contact@palletsprojects.com>"
]

# first element
$ dephell package show --filter="authors.first()" click
Armin Ronacher <armin.ronacher@active-4.com>

# last element
$ dephell package show --filter="authors.last()" click
Pallets Team <contact@palletsprojects.com>

# get element by index
$ dephell package show --filter="authors.0" click
Armin Ronacher <armin.ronacher@active-4.com>

# reverse list
$ dephell package show --filter="authors.reverse()" click
[
  "Pallets Team <contact@palletsprojects.com>",
  "Armin Ronacher <armin.ronacher@active-4.com>"
]

# get records count
$ dephell package show --filter="authors.len()" click
2
```

Work with items in list:

```bash
dephell package search author:orsinium
[
  {
    "description": "Work with python versions",
    "name": "dephell-pythons",
    "url": "https://pypi.org/project/dephell-pythons/",
    "version": "0.1.0"
  },
  ...
]

# get field from each record
$ dephell package search --filter="#.name" author:orsinium
[
  "dephell-discover",
  "pros",
  "homoglyphs",
  ...
]

# sort
$ dephell package search --filter="#.name.sort()" author:orsinium
[
  "advice",
  "aop",
  "deal",
  ...
]

# get a few fields
$ dephell package search --filter="#.name+description.each()" author:orsinium
[
  {
    "description": "Find project modules and data files (packages and package_data for setup.py).",
    "name": "dephell-discover"
  },
  {
    "description": "UNIX pipeline on python and steroids",
    "name": "pros"
  },
  ...
]
```
