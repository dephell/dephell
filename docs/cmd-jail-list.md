# dephell jail list

Shows a list of all packages installed by [dephell jail install](cmd-jail-install) and their endpoints.

```bash
$ dephell jail list
{
  "flake8": [
    "flake8"
  ],
  "httpie": [
    "http"
  ]
}
```

Output can be filtered by jail name:

```bash
$ dephell jail list --filter=httpie
[
  "http"
]
```

## See also

1. [How to filter commands JSON output](filters).
1. [dephell jail show](cmd-jail-show) to show more info about a particular jail.
1. [dephell jail install](cmd-jail-install) to create a new jail.
1. [dephell jail remove](cmd-jail-remove) to remove jail.
