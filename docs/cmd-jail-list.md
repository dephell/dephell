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
$ dephell jail list httpie
[
  "http"
]
```
