# dephell inspect project

Shows metainfo from the `from` dependency file, like project name, version, required python, etc.

```bash
$ dephell inspect project
{
  "description": "Dependency resolution for Python",
  "links": {
    "documentation": "https://dephell.org/docs/",
    "homepage": "https://dephell.org/",
    "repository": "https://github.com/dephell/dephell"
  },
  "name": "dephell",
  "python": ">=3.5",
  "version": "0.7.8"
}
```

## See also

1. [dephell project validate](cmd-project-validate) to check project metadata for compatibility issues and missed information.
1. [dephell inspect config](cmd-inspect-config) to get information about the project configuration.
