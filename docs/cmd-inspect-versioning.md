# dephell inspect versioning

Shows info about project versioning scheme and current version.

```bash
$ dephell inspect versioning
{
  "rules": {
    "supported": [
      "init",
      "local",
      "major",
      "minor",
      "patch",
      "pre",
      "premajor",
      "preminor",
      "prepatch",
      "release"
    ],
    "unsupported": [
      "dev",
      "post"
    ]
  },
  "scheme": "semver",
  "version": "0.7.9"
}
```

Read about schemes and rules in [dephell project bump](cmd-project-bump) docs.

## See also

1. [dephell project bump](cmd-project-bump) to bump project version.
1. [dephell inspect project](cmd-inspect-project) to get information about the project metainfo.
1. [dephell inspect config](cmd-inspect-config) to get information about the project configuration.
