# dephell package downloads

Get downloads statistic for package from [PyPI.org](https://pypi.org/). This command works with amazing [PyPI Stats](https://pypistats.org/) API, God bless this service.

```bash
$ dephell package downloads textdistance
{
  "pythons": [
    {
      "category": "35",
      "chart": "▅▂▄▃▁▂▄ ▇█▄▄▆█▄ ▂▂▄▅▁▁▄ ▅▄▅▄▁▁▄",
      "day": 120,
      "month": 3726,
      "week": 786
    },
    ...
  ],
  "systems": [
    {
      "category": "Linux",
      "chart": "▄▄▅▃▂▁█ ▇█▄▄▄▄▄ ▅▃▄▅▁▁▄ ▅▃▅▄▁▁▄",
      "day": 259,
      "month": 6947,
      "week": 1421
    },
    ...
  ],
  "total": {
    "day": 284,
    "month": 8751,
    "week": 1731
  }
}
```

## Fields

+ `pythons` -- statistic by python versions.
+ `systems` -- statistic by operating systems.
+ `total.day` -- total downloads yesterday.
+ `total.week` -- total downloads for previous 7 days.
+ `total.month` -- total downloads from yesterday to the same day in the previous month.
+ `pythons.#.chart` and `system.#.chart` -- downloads bar chart for last 28 days grouped by 7 days.
+ `pythons.#.day` and `system.#.day` -- total downloads yesterday.
+ `pythons.#.week` and `system.#.week` -- total downloads for previous 7 days.
+ `pythons.#.month` and `system.#.month` -- total downloads for previous 30 days.

## Filtering

This command, as all commands with JSON output, supports [filtering](filters). For example, get only month stat for pythons:

```bash
dephell package downloads textdistance --filter="pythons.#.category+month.each()"
[
  {
    "category": "27",
    "month": 332
  },
  ...
]
```

## See also

1. [How to filter commands JSON output](filters).
1. [dephell package show](cmd-package-show) to get information about package.
1. [dephell package search](cmd-package-search) to search packages on [PyPI](https://pypi.org/).
