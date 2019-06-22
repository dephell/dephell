# dephell jail try

Try python packages in an isolated environment.

Try [textdistance](https://github.com/orsinium/textdistance):

```bash
$ dephell jail try textdistance
INFO creating venv... (python=/usr/local/bin/python3.7, venv=/tmp/tmpgixqt4_q)
INFO build dependencies graph...
INFO installation... (executable=/tmp/tmpgixqt4_q/bin/python3.7, packages=1)
Collecting textdistance==4.1.3 (from -r /tmp/tmpduyecsir/requiements.txt (line 2))
Installing collected packages: textdistance
Successfully installed textdistance-4.1.3
INFO installed
INFO running...
Python 3.7.0 (default, Dec 24 2018, 12:47:36)
[GCC 5.4.0 20160609] on linux
Type "help", "copyright", "credits" or "license" for more information.
>>>
```

In this example DepHell installs latest `texdistance` release in a temporary virtual environment and runs python interpreter with already imported `textdistance` inside.

Use [ipython](https://ipython.org/) instead of standard python interpreter:

```bash
$ dephell jail try --command=ipython textdistance
```

Set python version:

```bash
$ dephell jail try --python=3.5 textdistance
...
Python 3.5.3 (928a4f70d3de, Feb 08 2019, 10:42:58)
[PyPy 7.0.0 with GCC 6.2.0 20160901] on linux
Type "help", "copyright", "credits" or "license" for more information.
>>>>
```

Install flake8 and plugin for it and run checks on given path:

```bash
$ dephell jail try --command="flake8 ./dephell" flake8 flake8-commas
```

## See also

1. [How DepHell choose Python interpreter](python-lookup).
1. [dephell jail install](cmd-jail-install) to install CLI tool in permanent jail.
1. [dephell venv create](cmd-venv-create) for information about virtual environments management in DepHell.
1. [dephell package install](cmd-package-install) to install package into project virtual environment.
1. [dephell deps install](cmd-deps-install) to install all project dependencies.
