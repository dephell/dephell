# dephell venv shell

Activates virtual environment of current project and environment for current shell. If virtual environment doesn't exist DepHell will create it.

Supported shells:

+ [cmd.exe](https://en.wikipedia.org/wiki/Cmd.exe)
+ [PowerShell](https://en.wikipedia.org/wiki/PowerShell)
+ [Bash](https://bit.ly/1ikp2Hl)
+ [Fish](https://fishshell.com/)
+ [Zsh](https://en.wikipedia.org/wiki/zsh)
+ [Xonsh](http://xon.sh/index.html)
+ [Tcsh](https://en.wikipedia.org/wiki/Tcsh)
+ [Csh](https://en.wikipedia.org/wiki/C_shell)

```bash
$ dephell venv shell --env=docs
```

This command build environment variables in the same way as [dephell venv run](cmd-venv-run).

## See also

1. [dephell venv run](cmd-venv-run) to run single command in a virtual environment.
