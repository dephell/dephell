# dephell venv entrypoint

The command creates a script in user bin dir that does the next things:

1. Export env vars that specified in `vars` dictionary in the config.
1. Sources dotenv file specified in `dotenv` configuration.
1. Changes current dir for the command on the project path.
1. Runs `command` in the `venv`.

Before making the script, the command also does a few more things:

1. Creates the given `venv` if it doesn't exist yet.
1. Installs the given executable from the `command` if it's not installed in the `venv` yet.

## Example

DepHell itself has the next section in `pyproject.toml`:

```toml
[tool.dephell.typing]
from = {format = "poetry", path = "pyproject.toml"}
command = "mypy --ignore-missing-imports --allow-redefinition dephell"
```

First of all, let's create a virtual environment and install dependencies:

```bash
$ dephell venv create --env=typing
$ dephell deps install --env=typing
```

And now we can expose entrypoint for the command:

```bash
$ dephell venv entrypoint --env=typing
WARNING executable is not found in venv, trying to install... (executable=mypy)
INFO build dependencies graph...
INFO installation... (executable=/home/gram/.local/share/dephell/venvs/dephell-nLn6/typing/bin/python3.8, packages=5)
Collecting mypy-extensions==0.4.3
Collecting typed-ast==1.4.1
Collecting typing-extensions==3.7.4.1
Collecting mypy==0.770
Installing collected packages: mypy-extensions, typed-ast, typing-extensions, mypy
Successfully installed mypy-0.770 mypy-extensions-0.4.3 typed-ast-1.4.1 typing-extensions-3.7.4.1
INFO installed
INFO script created (path=/home/gram/.local/bin/dephell-mypy)
```

MyPy isn't specified in `from` dependency file and wasn't installed by `dephell deps install`. So, `dephell venv entrypoint` does the installation by itself. Another thing to note is that the command has generated script name on the base of project name and the given executable (`dephell-mypy`). You can explicitly specify binary name to use:

```bash
dephell venv entrypoint --env=typing dephell-typing
```

Let's see what's inside the script (`cat /home/gram/.local/bin/dephell-mypy`):

```bash
#!/usr/bin/env bash
cd /home/gram/Documents/dephell
/home/gram/.local/share/dephell/venvs/dephell-nLn6/typing/bin/mypy --ignore-missing-imports --allow-redefinition dephell $@
```

Now we can call the given script from another project without changing dirs and poking around with environments:

```bash
dephell-mypy --help
```

## Use cases

1. Make a quick alias for a command you run really often. In the example above, we can type `dephell-mypy` instead of `dephell venv run --env=typing` and save a few precious seconds of life every day.
1. Create entrypoint to quickly get inside of project's [ipython](https://ipython.org/) shell on your production server: `dephell venv entrypoint --command=ipython`
1. Expose your project's entrypoint from it's venv into the system. Almost the same as [dephell jail install](cmd-jail-install) but for your local project.

## See also

1. [dephell venv create](cmd-venv-create) to create a venv.
1. [dephell deps install](cmd-deps-install) to install project deps in a venv.
1. [dephell venv run](cmd-venv-run) to run a command in a venv.
1. [dephell venv shell](cmd-venv-shell) to activate a venv for your current shell.
1. [dephell jail install](cmd-jail-install) to install a third-party CLI tool into a separate venv.
1. [dephell project register](cmd-project-register) to make the project importable from anywhere in your system.
