# Installation

Stable version

```bash
curl -L dephell.org/install | python3
```

It will install DepHell into DepHell's jail ([WE NEED TO GO DEEPER](https://knowyourmeme.com/memes/we-need-to-go-deeper)).

If installation script doesn't work:

```bash
python3 -m pip install --user dephell[full]
```

This command installs DepHell globally, without virtual environment. Extra `full` is optional and installs some dependencies that isn't required, but makes DepHell a little bit better. So, if you can't install by the recommend way and have some conflicts with your global modules, install without it:

```bash
python3 -m pip install --user dephell
```

## Get development version

Install dev version inside of site-packages:

```bash
curl -L dephell.org/install > install.py
python3 install.py --branch=master
```

Or get whole project and teach Python to use it:

```bash
$ git clone https://github.com/dephell/dephell.git
$ cd dephell
$ sudo python3 -m pip install -e .
```
