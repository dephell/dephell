# dephell package remove

Remove package without package dependencies:

```bash
$ dephell package remove homoglyphs
```

This command doesn't remove package dependencies because we can't be sure that these dependencies aren't used anywhere in your system. For example, you want to remove `requests` that has `urllib3` in the dependencies list. But also you have somewhere on your system your personal project that depends on `urllib3` too. So, we can't sure that we can remove it. If it is OK to you use [dephell package purge](cmd-package-purge).

## See also

1. [How DepHell choose Python environment](python-lookup).
1. [dephell package purge](cmd-package-purge) to remove package with dependencies.
1. [dephell package install](cmd-package-install) to install package into environment.
1. [dephell deps install](cmd-deps-install) to install all project dependencies.
1. [dephell jail install](cmd-jail-install) to install Python CLI tools into isolated virtual environment.
