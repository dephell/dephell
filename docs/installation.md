# Installation

Recommend way:

```bash
curl https://raw.githubusercontent.com/dephell/dephell/master/install.py | python3
```

It will install DepHell into DepHell's jail ([WE NEED TO GO DEEPER](https://knowyourmeme.com/memes/we-need-to-go-deeper)). However, this script experimental. So, in the project's README presented other way:

```bash
python3 -m pip install --user dephell[full]
```

This command installs DepHell globally, without virtual environment. Extra `full` is optional and installs some dependencies that isn't required, but makes DepHell a little bit better. So, if you can't install by the recommend way and have some conflicts with your global modules, install without it:

```bash
python3 -m pip install --user dephell
```

## Get development version

```bash
$ git clone https://github.com/dephell/dephell.git
$ cd dephell
$ sudo python3 -m pip install -e .
```
