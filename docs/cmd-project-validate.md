# dephell project validate

Validate project metadata that required to build good and compatible distribution package.

## Errors

+ "field is unspecified". Next fields should be specified and not empty:
    + name
    + version
    + license
    + keywords
    + classifiers
    + description
+ "bad name". Project name should be normalized.
+ "version should be str"
+ "cannot find Python files for package"
+ "short description is too long". Short description should be shorter than 140 chars.
+ "short description is too short". Short description should be longer than 10 chars.
+ "no authors specified"
+ "no links specified"
+ "no license specified in classifier"
+ "no development status specified in classifier"
+ "no python version specified in classifier"

## Warnings

+ "no dependencies found". Maybe, your project has no dependencies. Or maybe, you forgot to specify them.

## See also

1. [dephell project build](cmd-project-build) to build package for the project.
