# dephell project bump

Bump project version. Versioning scheme specified as `--versioning` and bumping rule or new version specified as positional argument. For example, bump minor version number by semver rules:

```bash
$ dephell project bump --versioning=semver minor
INFO generated new version (old=0.3.2, new=0.4.0)
INFO file bumped (path=/home/gram/Documents/dephell/dephell/__init__.py)
```

It's recommend to explicitly add `versioning` in config to let your users know which scheme you're using in your project:

```toml
[tool.dephell.main]
versioning = "semver"
```

Command steps:

1. Try to detect version from `from` file.
1. Try to detect version from project source code.
1. Generate new version.
1. Write new version in source code. DepHell looks for `__version__` variable in project source and writes new version in it.
1. Write new version in `from` file.

Also, the command adds git tag if `--tag` option (or `tag = <your_template>` in the config) is specified as template 
with `{new_version}` placeholder:

```bash
$ dephell project bump --tag 'v.{new_version}'
INFO generated new version (old=0.8.0, new=0.9.0)
INFO file bumped (path=/home/gram/Documents/dephell/dephell/__init__.py)
INFO commit and tag
INFO tag created, do not forget to push it: git push --tags
```

## Rules

1. `init` -- write initial version for current versioning scheme.
1. `major` or `breaking` -- increment first number of version. In `pep`, `semver`, and `comver` it means breaking changes that can broke third-party code that depends on your project. Example: `1.2.3` → `2.0.0`. Zero major version has special meaning: before `1.0.0` release any increment of `minor` number can break anything.
1. `minor` or `feature` -- increment second number of version. In `pep`, and `semver` it means non-breaking new features. Example: `1.2.3` → `1.2.0`.
1. `patch`, `fix` or `micro` -- increment third number of version. In `pep`, and `semver` it means bugfixes that don't add new features or break anything. For `calver` it usually means hotfixes that must be delivered ASAP. Example: `1.2.3` → `1.2.4`.
1. `pre`, `rc` or `alpha` -- increment pre-release number. Semantic depends on versioning scheme. A pre-release version indicates that the version is unstable and anything can be changed until release.
1. `premajor` -- applies both `pre` and `major`.  Example: `1.2.3` → `2.0.0-rc.1`
1. `preminor` -- applies both `pre` and `minor`.  Example: `1.2.3` → `1.3.0-rc.1`
1. `prepatch` -- applies both `pre` and `patch`.  Example: `1.2.3` → `1.2.4-rc.1`
1. `release` -- removes any pre-release number.  Example: `1.2.3-rc.1` → `1.2.3`
1. `post` -- increment post-release number. This is supported only by `pep`. Post-release number increment means some changes that do not affect the distributed software at all. For example, correcting an error in the release notes, metainfo, including license in the package etc.
1. `dev` -- increment `dev` number. Kind of pre-release that must not be used for any purposes except the project development. So, dev-releases should not be uploaded on public index servers. This version number also supported only by `pep`.
1. `local` -- increment local version number. This number separated from main version by `+`. See more details in the next section.

## Local number

1. Local number specified in `pep` and behave like post-release: `1.2+1` > `1.2`.
1. Be careful, local numbers compared as strings: `1.2+9` > `1.2+10`.
1. PEP recommends to use this number to indicate applying some patches to the release. For example, patch for compatibility with Ubuntu, with Django or with another project.
1. `semver` and `comver` allow to use "build metadata" with the same meaning as local number in `pep`. However, in `semver` and `comver` these metadata doesn't affect versions ordering. For example, `1.2+1 == 1.2`. For all Python projects all tools uses pep, so you shouldn't worry about it. Thence, DepHell allows you to use local number for `semver` and `comver` too.
1. Local number can contains any ASCII letters, digits and dot.
1. We recommend to use local number for nightly releases. It's like pre-release, but when you don't know version of future release and just add local number to the latest release version. See discussion in SemVer repository for more details: [Nightly builds not supported](https://github.com/semver/semver/issues/200)
1. When you specifying rule as `local`, DepHell just increments previous local number: 1 → 2 → 3... When you want to specify exact value for local version you can pass instead of rule `+` sign and local version number. For example, if your current version `1.2.3+1` and you run `dephell project bump +lol` your new version will be `1.2.3+lol`.

## Versioning schemes

1. [pep](https://www.python.org/dev/peps/pep-0440/#version-scheme) -- versioning scheme specified in PEP-420. Based on SemVer, but has much more features. All tools in Python (and DepHell too) parse projects versions by this PEP, so you can use it for your project and don't care about machines. However, this pep allows to make over-complicated versions that really difficult to understand for humans.
1. [semver](https://semver.org/) -- most recommend versioning scheme. Allows your users (and machines) by version easily understand when you have broken something in your project, have added some new features or have fixed some bugs. If you don't know what to use, use it.
1. [comver](https://github.com/staltz/comver) -- this is semver without `patch` number. All changes that don't broke anything increments `minor` version number. You can use it if in your project it's difficult to separate bug fixes and features.
1. [calver](https://calver.org/) -- it's when you use current date (year and month) instead of version. For example, `2018.12`. DepHell uses 4-numbers year as major number to explicitly indicate that your project uses CalVer. Also you can pass `micro` rule to add day in the version number. If previous release was today then `micro` rule will just increment this number. You can use this versioning if you don't want to care about versioning at all. However, this is strongly discouraged for any projects that can be used as dependency for third-party code.
1. [romver](http://dafoster.net/articles/2015/03/14/semantic-versioning-vs-romantic-versioning/) -- romantic versioning (not [Sentimental Versioning](http://sentimentalversioning.org/), please) is when humans and marketing more important for you than machines. Bumping `major`, `minor` or `patch` number shows importance of changes and says nothing about type of this changes. Every update can break everything. As calver, never use this versioning in tools that can be used in any third-party code. But it's OK for products for users like Firefox. DepHell allows only `major`, `minor` and `patch` rules for RomVer because this versioning for humans, and humans don't understand complicated combinations of `pre`, `post` and `local`.
1. [serial](https://packaging.python.org/guides/distributing-packages-using-setuptools/#serial-versioning) -- this is just single number that you increment for every release (1, 2, 3...). Simplest versioning scheme, but doesn't provide any information about release changes type. Avoid this scheme if possible.
1. [roman](https://en.wikipedia.org/wiki/Roman_numerals) -- roman numbers versioning. Never use it. It won't work after third release. However, you can try it for your internal project. Just for fun. Don't say anyone that I've recommended it to you.
1. [zerover](https://0ver.org/) -- kind of `semver`, but your `major` number always 0. Sounds like joke, but this is the best versioning for experimental projects that can broke anything in any release. So, if it's about your project then explicitly specify `zerover` versioning in your DepHell config. It says to your users that they can't upgrade without running quite strong integration tests.

## Projects that use these versioning schemes

1. semver:
    + [six](https://pypi.org/project/six/#history)
    + [botocore](https://pypi.org/project/botocore/#history)
    + [python-dateutil](https://pypi.org/project/python-dateutil/#history)
    + [requests](https://pypi.org/project/requests/#history)
    + [chardet](https://pypi.org/project/chardet/#history)
    + [rsa](https://pypi.org/project/rsa/#history)
1. comver:
    + [PyYAML](https://pypi.org/project/PyYAML/#history)
    + [idna](https://pypi.org/project/idna/#history)
    + [terminator](https://launchpad.net/terminator)
1. calver:
    + [pytz](https://pypi.org/project/pytz/#history)
    + [certify](https://pypi.org/project/certifi/#history)
    + [PyCharm](https://www.jetbrains.com/pycharm/download/previous.html)
    + [Ubuntu](http://releases.ubuntu.com/)
1. romver:
    + [pip](https://pypi.org/project/pip/#history) (`1.5.6` → `6.0`)
    + [pipenv](https://pypi.org/project/pipenv/#history) (`0.2.8` → `3.0.0`)
1. roman:
    + [Mac OS X](https://en.wikipedia.org/wiki/MacOS)
    + [WordPerfect Office](https://en.wikipedia.org/wiki/WordPerfect#WordPerfect_Office)
    + [3.V album by Zebra band](https://en.wikipedia.org/wiki/3.V)
    + [состояние птиц](https://bsos.bandcamp.com/)
1. zerover:
    + [html5lib](https://github.com/html5lib/html5lib-python/issues/282) 0.999999999
    + [docutils](https://pypi.org/project/docutils/#history) 0.14 (16 years from first release)
    + [pyasn1](https://pypi.org/project/pyasn1/#history) 0.4.5 (13 years from first release)
    + [pandas](https://pypi.org/project/pandas/#history) 0.24.2 (10 years from first release)
    + [colorama](https://pypi.org/project/colorama/#history) 0.4.1 (9 years from first release)
    + See more 0ver projects on [0ver.org](https://0ver.org/#notable-zerover-projects).

## Command examples

SemVer:

```bash
$ dephell project bump init
INFO generated new version (old=0.0.0, new=0.1.0)

$ dephell project bump fix
INFO generated new version (old=0.1.0, new=0.1.1)

$ dephell project bump minor
INFO generated new version (old=0.1.1, new=0.2.0)

$ dephell project bump major
INFO generated new version (old=0.2.0, new=1.0.0)

$ dephell project bump pre
INFO generated new version (old=1.0.0, new=1.0.0-rc.1)

$ dephell project bump post
ERROR ValueError: rule post is unsupported by scheme semver

$ dephell project bump local
INFO generated new version (old=1.0.0-rc.1, new=1.0.0-rc.1+1)

$ dephell project bump +ubuntu1
INFO generated new version (old=1.0.0-rc.1+1, new=1.0.0-rc.1+ubuntu1)
```

CalVer:

```bash
$ dephell project bump --versioning=calver init
INFO generated new version (old=1.0.0-rc.1+ubuntu1, new=2019.4)

# today
$ dephell project bump --versioning=calver micro
INFO generated new version (old=2019.4, new=2019.4.9)

# if execute `micro` again: today + 1
$ dephell project bump --versioning=calver micro
INFO generated new version (old=2019.4.9, new=2019.4.10)
```

PEP:

```bash
$ dephell project bump --versioning=pep init
INFO generated new version (old=2019.4.10, new=0.1.0)

$ dephell project bump --versioning=pep pre
INFO generated new version (old=0.1.0, new=0.1.0rc1)

$ dephell project bump --versioning=pep post
INFO generated new version (old=0.1.0rc1, new=0.1.0.post1)

# `dev` can be attached to `pre` or `post` too
$ dephell project bump --versioning=pep dev
INFO generated new version (old=0.1.0.post1, new=0.1.0.post1.dev1)
```

ZeroVer:

```bash
$ dephell project bump --versioning=zerover major
ERROR ValueError: rule major is unsupported by scheme zerover

$ dephell project bump --versioning=zerover minor
INFO generated new version (old=0.3.2, new=0.4.0)
```

Roman:

```bash
$ dephell project bump --versioning=roman init
INFO generated new version (old=0.3.2, new=I)

$ dephell project bump --versioning=roman major
INFO generated new version (old=I, new=II)
```

Custom version:

```bash
$ dephell project bump 0.3.2
INFO generated new version (old=0.1.0.post1.dev1, new=0.3.2)
```
