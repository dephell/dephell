# dephell generate license

Add LICENSE file in the project. This command gets the license name as input, downloads license template, substitutes current year and current system user name and saves result into LICENSE file.

```bash
$ dephell generate license MIT
$ dephell generate license Apache-2.0
```

## Which license should I choose?

For open source software use [MIT License](https://en.wikipedia.org/wiki/MIT_License). For proprietary software pay to a lawyer to help you make right choose in your case. You can discover other licenses on the [choosealicense.com](https://choosealicense.com/), but all of them has some limitations in real world that can harm your project:

1. [Apache 2.0](https://en.wikipedia.org/wiki/Apache_License) cool license, but requires you to insert license notice at the beginning of every source code file in the project. Also, Apache 2.0 requires all contributors to track all changes in a special file (usually named CHANGELOG). It takes some time that you can spendmore effective. There are some special tools that allow you to [generate CHANGELOG](https://stackoverflow.com/a/23047890/8704691) and [insert copyright notice](https://github.com/licenses/lice) in source files, but so.
1. [GNU GPLv3](https://en.wikipedia.org/wiki/GNU_General_Public_License#Version_3) forbid to use your project in proprietary projects. It useful when you want to make open source only for open source, but really limit your project popularity and usage. Almost all developers writes some proprietary software, and only a bit dvelopers get paid for open source. So, don't forbid your users to use your code.
1. [The Unlicense](https://en.wikipedia.org/wiki/Unlicense) and [WTFPL](https://en.wikipedia.org/wiki/WTFPL) have limitations on usage in some countries. Don't use them.
1. Most of your users don't know about other licenses like [Mozilla Public License](https://en.wikipedia.org/wiki/Mozilla_Public_License). Don't force them to read about new licenses specially for your project. Please, value their time.

## See also

1. [dephell deps licenses](cmd-deps-licenses) to show licenses for all project dependencies.
1. [dephell generate authors](cmd-generate-authors) to make AUTHORS file for project.
