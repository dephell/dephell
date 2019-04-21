# dephell generate travis

Adds `.travis.yml` config for your project.

1. If your `main` env has lockfile as `to` format, DepHell adds [audit](cmd-deps-audit) and [outdated](cmd-deps-outdated) checks. Also, DepHell marks they as `allow_failures` because these command can produce false-positive alerts. So, we don't want to fail whole your CI besause of it.
1. If some env has `pytest` command than this env will be ran on next envs:
    1. Linux: Python 3.5, 3.6, 3.7.
    1. Mac OS: Python 3.6.
1. If some envs has `command` specified (not `pytest`) then DepHell will make env for them too.

Of course, this file has to be manually validated and cleaned before running on CI. However, this is good bootstrap. If command doesn't work to you then use config example below to configure it on your own.

Output example:

```yaml
# Config for Travis CI, tests powered by DepHell.
# https://travis-ci.org/
# https://github.com/dephell/dephell

language: python

before_install:
  # show a little bit more information about environment
  - sudo apt-get install -y tree
  - env
  - tree
  # install DepHell
  # https://github.com/travis-ci/travis-ci/issues/8589
  - curl https://raw.githubusercontent.com/dephell/dephell/master/install.py | /opt/python/3.6/bin/python
  - dephell inspect self
install:
  - dephell venv create --env=$ENV --python="/opt/python/$TRAVIS_PYTHON_VERSION/bin/python"
  - dephell deps install --env=$ENV
script:
  - dephell venv run --env=$ENV

matrix:
  allow_failures:
    - name: security
    - name: outdated

  include:
    - name: security
      install:
        - "true"
      script:
        - dephell deps audit
    - name: outdated
      install:
        - "true"
      script:
        - dephell deps outdated

    - python: "3.6"
      env: ENV=flake8

    - python: "3.6"
      env: ENV=typing

    - python: "3.5"
      env: ENV=pytest
    - python: "3.6"
      env: ENV=pytest
    - python: "3.7-dev"
      env: ENV=pytest
    - python: "pypy3.5"
      env: ENV=pytest

    - os: osx
      language: generic
      env: ENV=pytest
      before_install:
        - curl https://raw.githubusercontent.com/dephell/dephell/master/install.py | /usr/local/bin/python3
        - dephell inspect self
      install:
        - dephell venv create --env=$ENV --python=/usr/local/bin/python3
        - dephell deps install --env=$ENV
```


## See also

1. [dephell generate config](cmd-generate-config) to make DepHell config for project.
