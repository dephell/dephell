# dephell vendor download

Download and extract project dependencies in a given directory.

```bash
dephell vendor download --from=requirements.txt --vendor-path=my_project/_vendor/
```

Some packages can be nightly and not ready for vendorization. So, you can exclude them:

```toml
[tool.dephell.vendorized]
from = {format = "pip", path = "requirements.txt"}

[tool.dephell.vendorized.vendor]
path = "my_project/_vendor"
exclude = ["jinja2", "setuptools"]
```

And then:

```bash
dephell vendor download --env=vendorized
```

How to find out packages that can't be vendorized? Do experiment:

1. `git checkout .`
1. Vendorize.
1. [Patch imports](cmd-vendor-import)
1. Try to run your project.
1. Have `ImportError` or `AttributeError`? Add this package into `exclude` list and try again.

## See also

1. [vendor commands index](index-vendor) to read more about vendorization.
1. [dephell vendor import](cmd-vendor-import) to patch all imports in your project.
