# dephell project upload

Upload project dist archives on [PyPI](https://pypi.org) or another pypi-compatible storage.

## Upload on pypi.org

First of all, register on [PyPI](https://pypi.org) and add your credentials:

```bash
dephell self auth pypi.org my_username my_password
```

**Pro tip**: add a space before the command and bash won't store it in the history ([read more](https://stackoverflow.com/a/29188490)).

Don't forget [bump project version](cmd-project-bump) and [build dist archives](cmd-project-build). And after that you can upload created dist archives on PyPI:

```bash
dephell project upload
```

## Upload on test.pypi.org

[TestPyPI](https://test.pypi.org/) is an ephemeral instance that allows you to experiment a bit with uploading and installing of your package. Specify `upload.url` as `test` or `test.pypi.org` to use it:

```bash
dephell project upload --upload-url=test
```

## Upload in a private repository

For example, upload on [Artifactory](https://jfrog.com/artifactory/)):

```bash
$ dephell self auth artifactory.example.com "my-mail@example.com" "my-secret-api-key"
dephell project upload --upload-url="https://rtifactory.example.com/artifactory/api/pypi/pypi-internal"
```

## API Token

To keep your PyPI password secure you can generate [API token](https://pypi.org/help/#apitoken) in your [account settings](https://pypi.org/manage/account/) and use it instead:

```bash
dephell self auth pypi.org "__token__" "pypi-my-secret-token"
```

This is required if you're using 2FA on PyPI.

## Dist files lookup

DepHell gets project name and version from the `from` dependency file and makes on the base of it pattern to find dist files in `dist` directory in the project root. So, `from` config option is required for this command. If you have no [dephell config](config), you have to explicitly specify it:

```bash
dephell project upload --from=setup.py
```

Or better is explicitly specify dist file:

```bash
$ dephell project upload --from-format=sdist --from-path=./dist/release-name.tar.gz
$ dephell project upload --from-format=wheel --from-path=./dist/release-name.whl
```

## See also

1. [Configuration and parameters](cmd-self-auth) to understand how DepHell configuration works.
1. [dephell project bump](cmd-project-bump) to bump project version.
1. [dephell project build](cmd-project-build) to build release dist packages.
1. [dephell self auth](cmd-self-auth) to provide credentials for the command.
