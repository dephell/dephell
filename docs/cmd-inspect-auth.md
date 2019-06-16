# dephell inspect auth

Shows all [added credentials](cmd-auth).

```bash
$ dephell auth example.com gram "p@ssword"
INFO credentials added (hostname=example.com, username=gram)

$ dephell inspect auth
[
  {
    "hostname": "example.com",
    "password": "p@ssword",
    "username": "gram"
  }
]
```

Use [filters](filters) to remove passwords from output:

```bash
$ dephell inspect auth --filter="#.hostname+username.each()"
[
  {
    "hostname": "example.com",
    "username": "gram"
  }
]
```

## See also

1. [dephell auth](cmd-auth) to add new credentials.
1. [dephell inspect config](cmd-inspect-config) to show all other params in the config.
