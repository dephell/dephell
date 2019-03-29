# dephell venv create

Create virtual environment for current project and environment. Always create virtual environment before executing [dephell deps install](cmd-deps-install) or [dephell install](cmd-install) if you want them to install packages into special virtual environment. Otherwise, these commands will use your current virtual environment (or global interpreter).

For example, create virtual environment for `docs` environment of current project:

```bash
$ dephell venv create --env=docs
```
