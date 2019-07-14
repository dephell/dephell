# dephell docker tags

Get available tags for a docker repository on [Docker Hub](https://hub.docker.com/). Use [filters](filters) to get only last 10 tags:

```bash
$ dephell docker tags --docker-repo=elasticsearch --filter=:10
WARNING cannot find config file
[
  "7.2.0",
  "6.8.1",
  "7.1.1",
  "7.1.0",
  "6.8.0",
  "7.0.1",
  "6.7.2",
  "7.0.0",
  "6.7.1",
  "5-alpine"
]
```

## See also

1. [How filters work](filters)
1. [dephell docker create](cmd-docker-create) to create a new container.
