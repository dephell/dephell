# dephell auth

Manage credentials: add, update, remove. These credentials are used for [Basic HTTP authentication](https://en.wikipedia.org/wiki/Basic_access_authentication) for [custom PyPI repositories](https://www.python.org/dev/peps/pep-0503/).

Add new credentials:

```bash
$ dephell auth pypi.example.com my-useranme "my-p@ssword"
INFO credentials added (hostname=pypi.example.com, username=my-useranme)
```

Remove credentials for user:

```bash
$ dephell auth pypi.example.com my-useranme
INFO credentials removed (hostname=pypi.example.com, username=my-useranme)
```

Remove credentials for all users for given hostname:

```bash
$ dephell auth pypi.example.com
INFO credentials removed (hostname=pypi.example.com, count=1)
```

Credentials are stored in global config. If you add credentials for `example.com`, they will be used in all projects to connect to `example.com`.

## See also

1. [Private PyPI repository](use-warehouse) usage details and examples.
1. [dephell inspect auth](cmd-inspect-auth) to list added credentials.
1. [dephell deps install](cmd-deps-install) to install dependencies from private repository.
