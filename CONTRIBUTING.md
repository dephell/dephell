# Contributing to dephell

Thank you for deciding to contribute to DepHell!  This guide is to assist you with contributing code.  If you have a question that isn't answered here, please [open an issue][open issue].

## The basics

So you want to contribute some code?  Great! Here are the basic steps:

1. Find an [issue][issues] that you want to work on. Good places to start are [good first issues] or [help wanted]. You could also [open an issue][open issue] if there is something specific you want to contribute. Wait for a response before you start coding though, as the thing you want might already exist somewhere!
1. Fork DepHell.
1. Clone your fork.
1. Create a branch to work against.
1. Run tests to make sure they work for your system.
1. Write some tests.
1. Write some code.
1. Run tests to make sure it works.
1. Run flake8 checks.
1. Write some docs.
1. Push your branch (to your fork).
1. Create a pull request to dephell/master
1. Wait for checks to run and fix anything that was wrong

## Testing

Any new code that you contribute will be ideally covered under an automated test. To run existing tests:

```bash
dephell venv create --env pytest
dephell deps install --env pytest
dephell venv run --env pytest
```

To write new tests using [pytest], place them in the `tests` directory.  This directory should roughly follow the same file structure as the source directory (`dephell`) except that every file/module is prepended with `test_`.  For example, the file containing tests for `dephell/commands/deps_convert.py` is `tests/test_commands/test_deps_convert.py`.

## Style

All the code you contribute must follow the same style as the rest of dephell:

- Follow [PEP8]
- Use `'single quotes'` for strings, not `"double quotes"`

Run flake8 to see how you're doing:

```bash
dephell venv create --env flake8
dephell deps install --env flake8
dephell venv run --env flake8
```

Main things you contribute are ideas and implementation. So, if you struggled with flake8 checks, don't worry, just ask help of maintainers in comments to your Pull Request. If your code passed CI, merging of Pull Request can't be rejected or delayed because of style. No [bikeshedding](https://en.wikipedia.org/wiki/Law_of_triviality) and meaningless discussions.

## Using an IDE

If you want to use an IDE to edit / test dephell code, you'll have to point that IDE to the virtual environment dephell created.  You can either get this path using `dephell inspect venv` or create the venv in a directory your IDE will find (e.g. `dephell venv create --venv .venv`).  Some tests currently assume they are being run from the root of the project.  If your IDE likes to run tests from other directories, you may need to update some existing tests to use relative paths.

[issues]: https://github.com/dephell/dephell/issues?utf8=✓&q=is%3Aissue+is%3Aopen+
[open issue]: https://github.com/dephell/dephell/issues/new
[help wanted]: https://github.com/dephell/dephell/issues?q=is%3Aissue+is%3Aopen+label%3A%22help+wanted%22
[good first issues]: https://github.com/dephell/dephell/issues?q=is%3Aissue+is%3Aopen+label%3A%22good+first+issue%22

[pytest]: https://docs.pytest.org/en/latest/
[PEP8]: https://www.python.org/dev/peps/pep-0008/
