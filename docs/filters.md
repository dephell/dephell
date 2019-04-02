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

## Filters

Filters separated by `.` or `-` and can be one of the following type:

+ Field name to get some field from dict output.
+ Sum of fields. Will return dictionary with given fields. For example, `name+license` will return `{"license": "BSD-2-Clause", "name": "click"}`.
+ Index to get some element from list output.
+ Slice to get set of elements from list output. For example:
    + `:10` to get first 10 elements,
    + `10:` to drop out first 10 elements,
    + `2:5` to get elements with indices 2, 3 and 4.
+ Function to process output.

Functions:

+ `each()` or `#` -- convert list of dicts to dict of lists or otherwise. For example, `[{a: 1, b: 2}, {a: 3, b: 4}]` will be converted into `{a: [1, 3], b: [2, 4]}`.
+ `first()` or `0` -- get first element from list.
+ `last()` or `latest()` -- get last element from list.
+ `len()`, `length()` or `size()` -- get count of elements in a list.
+ `max()` -- get maximum value from a list.
+ `min()` -- get minimum value from a list.
+ `reverse()` or `reversed()` -- reverse values in a list.
+ `sort()` or `sorted()` -- sort values in a list.
+ `type()` -- get value type.
+ `zip()` -- transpose output. `[[a, b], [c, d], [e, f]]` will be converted into `[[a, c, e], [b, d, f]]`.

First filter gets command output. Next filters get output from previous filter.

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

# get only first 10 elements for previous filter:
$ dephell package search --filter="#.name+description.each().:10" author:orsinium
```

## Alternatives

In some rare cases you could want to specify some complex filter that not covered by DepHell. So, you can process DepHell output into some other command that can process JSON. Some of them:

+ [jq](https://stedolan.github.io/jq/)
+ [jj](https://github.com/tidwall/jj)
+ [jd](https://github.com/tidwall/jd)

Also, it's recommend for better processing to disable INFO-messages and progress bars. For example:

```bash
$ dephell deps licenses --level=WARNING --silent | jq --compact-output '."Apache-2.0"'
["aiofiles","aiohttp",...]
```
