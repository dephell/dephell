# dephell vendor import

Patch all imports in your project and vendorized dependencies itself to use these vendorized dependencies. For example, if you're using `requests` third-party library and have `my_project/_vendor/requests` directory, run the next command:

```bash
dephell vendor import --vendor-path=my_project/_vendor/
```

After that all imports of `requests` inside `my_project` will be patched to import `my_project._vendor.requests` instead.

Python import system makes a big difference between packages and subpackages, and what worked in library itself can be broken when you place this library inside your project. So, be ready to exclude some libraries from vendorization. Read about it in [dephell vendor download](cmd-vendor-download) documentation.

## See also

1. [vendor commands index](index-vendor) to read more about vendorization.
1. [dephell vendor download](cmd-vendor-download) to download your project dependencies in some directory.
