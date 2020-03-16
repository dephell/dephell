# dephell package verify

Verify GPG signature for a release from [PyPI](https://pypi.org/).

Verify files for the latest release:

```json
$ dephell package verify flask
INFO getting release file... (url=https://files.pythonhosted.org/packages/.../Flask-1.1.1-py2.py3-none-any.whl)
{
  "created": "2019-07-08",
  "fingerprint": "AD253D8661D175D001F462D77A1C87E3F5BC42A8",
  "key_id": "7A1C87E3F5BC42A8",
  "name": "Flask-1.1.1-py2.py3-none-any.whl",
  "release": "1.1.1",
  "status": "signature valid",
  "username": "David Lord <davidism@gmail.com>"
}

INFO getting release file... (url=https://files.pythonhosted.org/packages/.../Flask-1.1.1.tar.gz)
{
  "created": "2019-07-08",
  "fingerprint": "AD253D8661D175D001F462D77A1C87E3F5BC42A8",
  "key_id": "7A1C87E3F5BC42A8",
  "name": "Flask-1.1.1.tar.gz",
  "release": "1.1.1",
  "status": "signature valid",
  "username": "David Lord <davidism@gmail.com>"
}
```

Verify files for the given release:

```bash
dephell package verify django==2.0.1
```

Note that packages signing isn't popular in Python world. Most of packages have no signature:

```bash
$ dephell package verify pip
ERROR no signed files found
```

## See also

1. [How to filter commands JSON output](filters).
1. [dephell package show](cmd-package-show) to show information about single package.
1. [dephell deps audit](cmd-deps-audit) to find known vulnerabilities in the project dependencies.
