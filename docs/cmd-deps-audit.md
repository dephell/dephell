# dephell deps audit

Returns list of known vulnerabilities for your dependencies.

This command returns non-zero code if some vulnerabilities was found, so you can use it on CI.

## Sources

[pyup.io](https://pyup.io/) provides public repository [safety-db](https://github.com/pyupio/safety-db) with all vulnerabilities in their database. DepHell uses it. This repository automatically updates every month. So, if you want to get actual reports you have to use their official solutions. They provide Safety CI that [free for Open Source](https://pyup.io/pricing/) and $30 for personal usage. If you have "Business" plan you also can get API key and use their [official CLI](https://github.com/pyupio/safety).

We used [snyk.io](https://snyk.io/) before, but now they have removed RSS feed.

## Dependencies lookup

1. If some package and version explicitly specified then this package will be used. Example: `dephell deps audit jinja2==2.0`.
1. If `to` format is a lockfile (`piplock`, `pipfilelock` or `poetrylock`) dependencies from this file will be used.
1. If `to` isn't specified and `from` is a lockfile dependencies from this file will be used.
1. Otherwise it uses common [Python environment lookup](python-lookup). TL;DR: project venv, current venv, python from config, python from dependencies file, current interpreter.

## Examples

Audit dependencies:

```bash
$ dephell deps audit
[
  {
    "current": "2.10",
    "description": "Sandbox Escape in jinja2 (pip) with medium severity ",
    "latest": "2.10.1",
    "links": [
      "https://pypi.org/project/Jinja2/",
      "https://palletsprojects.com/blog/jinja-2-10-1-released",
      "https://snyk.io/vuln/SNYK-PYTHON-JINJA2-174126"
    ],
    "name": "jinja2",
    "updated": "2019-04-06",
    "vulnerable": "<2.10.1"
  }
]
```

Audit a package:

```bash
$ dephell deps audit jinja2==2.0
[
  {
    "current": "2.0",
    "description": "jinja2 2.7.2 fixes a security issue: Changed the default folder for the filesystem cache to be user specific and read and write protected on UNIX systems.  See  for more information.",
    "latest": "2.10.1",
    "links": [
      "http://bugs.debian.org/cgi-bin/bugreport.cgi?bug=734747"
    ],
    "name": "jinja2",
    "updated": "2019-04-06",
    "vulnerable": "<2.7.2"
  },
  ...
]
```

Show only descriptions:

```bash
$ dephell deps audit --filter="#.description" jinja2==2.0
[
  "jinja2 2.7.2 fixes a security issue: Changed the default folder for the filesystem cache to be user specific and read and write protected on UNIX systems.  See  for more information.",
  "The default configuration for bccache.FileSystemBytecodeCache in Jinja2 before 2.7.2 does not properly create temporary files, which allows local users to gain privileges via a crafted .cache file with a name starting with __jinja2_ in /tmp.",
  "Sandbox Escape in jinja2 (pip) with medium severity "
]
```

Show only links:

```bash
$ dephell deps audit --filter="#.links.flatten()" jinja2==2.0
[
  "http://bugs.debian.org/cgi-bin/bugreport.cgi?bug=734747",
  "https://nvd.nist.gov/vuln/detail/CVE-2014-1402",
  "https://pypi.org/project/Jinja2/",
  "https://palletsprojects.com/blog/jinja-2-10-1-released",
  "https://snyk.io/vuln/SNYK-PYTHON-JINJA2-174126"
]
```

See [filtering documentation](filters) for more information how to work with JSON output.

## See also

1. [How DepHell choose Python environment](python-lookup).
1. [How to filter commands JSON output](filters).
1. [dephell deps outdated](cmd-deps-outdated) to find outdated dependencies.
1. [dephell package list](cmd-package-list) to show information about installed packages.
1. [dephell package show](cmd-package-show) to get information about package.
